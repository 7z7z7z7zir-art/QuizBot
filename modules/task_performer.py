import sqlite3
import asyncio

from telegram import Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import modules.long_texts as long_texts
from .united import UserStates, Tasks, TemporaryUser


class TaskPerformer:
	def __init__(self, bot, token):
		self.bot = bot
		self.token = token
		self.users = {}
		self.inline_processing = {}

		self.database: sqlite3.Connection | None = None
		self.cursor: sqlite3.Cursor | None = None

		self.lock = asyncio.Lock()

		wellcome_texts = long_texts.wellcome_text

		self.wellcom_texts = {
			"normal": wellcome_texts["normal"],
			"student": wellcome_texts["student"],
			"teacher": wellcome_texts["teacher"],
			"admin": wellcome_texts["admin"]
		}

		self.return_menu_inline = {
			"normal": [
				[("ثبت نام در کلاس‌ها", "register_for_classes:DNRTUO")],
				[("ثبت‌نام به عنوان دبیر", "register_for_teacher:DNRTUO")]
			],

			"student": [
				[("نمایش کلاس‌های من", "display_student_classes:DNRTUO")],
				[("نمایش آزمون‌ها", "display_student_quizs:DNRTUO")],
				[("نمایش نتایج آزمون‌های قبلی", "display_previous_quiz_results:DNRTUO")],
				[("ثبت نام در کلاس‌ها", "register_for_classes:DNRTUO")]
			],

			"teacher": [
				[("نمایش کلاس‌های من", "display_teacher_classes:DNRTUO")],
				[("نمایش آزمون‌ها", "display_teacher_quizs:DNRTUO")],
				[("ثبت‌نام در کلاس‌های دیگر", "register_for_teacher:DNRTUO")]
			],

			"admin": [
				[
					("نمایش دبیران", "display_teachers:DNRTUO"),
					("نمایش دانش‌آموزان", "display_students:DNRTUO")
				],
				[("نمایش کلاس‌ها", "display_classes:DNRTUO:admin")],
				[("مدیریت درخواست‌های عضویت", "managing_membership_requests:DNRTUO")]
			]
		}

		for key in self.return_menu_inline.keys():
			self.return_menu_inline[key].append(
				[("درباره ما", "about:DNRTUO:normal")]
			)

	def create_inline_keyboard(self, inline):
		"""تبدیل ساختار منو به InlineKeyboardMarkup"""

		keyboard = []

		for row in inline:
			buttons = []

			for text, callback_data in row:
				buttons.append(
					InlineKeyboardButton(
						text=text,
						callback_data=callback_data
					)
				)

			keyboard.append(buttons)

		return InlineKeyboardMarkup(keyboard)

	def requires_role(self, user_role: str, required_role: str) -> bool:
		"""
		بررسی دسترسی کاربر بر اساس نقش.

		خروجی:
			True: دسترسی مجاز است.
			False: دسترسی مجاز نیست.
		"""

		role_hierarchy = {
			"normal": 0,
			"student": 1,
			"teacher": 2,
			"admin": 3
		}

		user_level = role_hierarchy.get(user_role)
		required_level = role_hierarchy.get(required_role)

		if user_level is None or required_level is None:
			return False

		return user_level >= required_level

	async def start(self, message: Message):
		"""هندل دستور /start"""

		role = self.get_user_role(message.chat.id)

		inline = self.return_menu_inline.get(role, [])
		welcome_text = self.wellcom_texts.get(role)

		keyboard = self.create_inline_keyboard(inline)

		await message.reply_text(
			text=welcome_text,
			reply_markup=keyboard
		)

	async def back_to_menu(self, message: Message):
		"""بازگشت به منو"""

		role = self.get_user_role(user_id=message.chat.id)

		inline = self.return_menu_inline.get(role, [])

		keyboard = self.create_inline_keyboard(inline)

		try:
			del self.users[message.chat.id]
		except KeyError:
			pass

		await message.edit_text(
			text=self.wellcom_texts.get(role),
			reply_markup=keyboard
		)

	def get_user_role(self, user_id: int):
		"""
		نقش کاربر را از دیتابیس دریافت می‌کند.

		خروجی:
			'admin'   : مدیر
			'teacher' : دبیر
			'student' : دانش‌آموز
			'normal'  : کاربر ثبت‌نام‌نشده
		"""

		self.cursor.execute(
			"SELECT role FROM users WHERE user_id = ?",
			(user_id,)
		)

		result = self.cursor.fetchone()

		if result is None:
			return "normal"

		return result[0]

	async def rename_class(self, message: Message):
		user_id = message.chat.id

		user: TemporaryUser = self.users.get(user_id)

		if user is None:
			return

		user_state = user.state

		if user_state == UserStates.NAME:

			name = message.text.strip()

			current_name = user.data["current_class_name"]
			class_id = user.data["class_id"]

			async with self.lock:
				self.cursor.execute(
					"UPDATE classes SET class_name = ? WHERE class_id = ?",
					(name, class_id)
				)

				self.database.commit()

			await message.reply_text(
				f"نام کلاس با موفقیت تغییر کرد!\n"
				f"نام قبلی: *{current_name}* و نام جدید: *{name}*",
				parse_mode="Markdown"
			)

			del self.users[user_id]

	async def create_new_quiz(self, message: Message):
		user_id = message.chat.id

		user: TemporaryUser = self.users.get(user_id)

		if user is None:
			return

		user_state = user.state

		if user_state == UserStates.START:
			pass

		elif user_state == UserStates.TITLE:
			pass

		elif user_state == UserStates.FINAL_APPROVAL:
			pass

		if user_state == UserStates.FINAL:
			pass