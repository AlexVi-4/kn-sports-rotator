# Padel Rotator Context
- Стек: Streamlit, Pandas, st-gsheets-connection.
- БД: Google Sheets (листы Players и Rotations).
- Безопасность: Вход по ADMIN_PASSCODE и USER_PASSCODE из st.secrets.
- Текущие задачи:
  1. Табличный вид расписания (st.table).
  2. Календарь и просмотр сохраненных ротаций.
  3. Боковая панель: счетчик и кнопка «Generate» расположен перед полем поиска multiselect.