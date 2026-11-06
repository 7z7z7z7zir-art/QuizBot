import time

class UserStates:
	START = "START"
	NONE = "NONE"
	USER_NAME = "USER_NAME"
	NAME = "NAME"
	USER_ID = "user_id"
	FULL_NAME = "full_name"
	TITLE = "title"
	FINAL_APPROVAL = "final_approval"
	FINAL = "final"
	
class Tasks:
	NONE = "NONE"
	RENAME_CLASS = "RENAME_CLASS"
	CREATE_NEW_QUIZ = "CREATE_NEW_QUIZ"
	
class TypesInline:
	"""با توجه به نیازم، دکمه‌های inline را به دو دسته تقسیم کردم"""
	RTUO = "RTUO" #مخفف Requires a 'temporary user' object
	DNRTUO = "DNRTUO" #مخفف Does not require a "temporary user" object

class TemporaryUser:
	"""برای گفت‌وگو های چند مرحله‌ای لازم می‌شود وضعیت کاربر به طور موقت ذخیره شود."""
	__slots__ = ["type_task", "state", "processing", "data", "last_change_time", "waiting_time", "ids"]
	def __init__(self, type_task: str, state: str=UserStates.START):
		self.type_task: str = type_task #نوع گفت‌وگو
		self.state: str = state #وضعیت(مرحله گفت‌وگو)
		self.ids = [] #برای قاطی نشدن با دکمه های RTUO گفت‌وگو های دیگر
		self.processing: bool = False #اگر برای این کاربر پردازشی درحال انجام باشد، True می‌شود تا از پردازش تکراری جلوگیری شود.
		self.data: dict = {} #اطلاعات موقت مثل سبد خرید
		self.last_change_time: int = time.time() #آخرین زمان/تاریخ فعالیت کاربر. به ثانیه
		self.waiting_time: int = 1_800 #اگه نیم ساعت فعالیتی نداشته باشد، حذف شود.
