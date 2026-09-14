from aiogram.fsm.state import State, StatesGroup

class CourseStates(StatesGroup):
    # Пользовательские
    main_menu = State()
    about_course = State()
    free_material = State()
    tariffs = State()
    tariff_selected = State()
    payment = State()
    payment_check = State()
    access_granted = State()
    my_access = State()
    my_purchase = State()
    faq = State()
    support = State()
    
    # Админские
    admin = State()
    admin_find_user = State()
    admin_give_access = State()
    admin_edit_setting = State()
    admin_mailing = State()
    admin_mailing_confirm = State()
    admin_remind_interval = State()