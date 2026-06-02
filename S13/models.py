from datetime import datetime
from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, BooleanField, Check
)

db = SqliteDatabase('work_program.db')


class BaseModel(Model):
    class Meta:
        database = db


class WorkProgram(BaseModel):
    """Основная сущность: рабочая программа дисциплины.
    discipline_id — внешний ID из Discipline Service, не хранится локально.
    Валидация существования discipline_id выполняется на уровне сервиса."""
    id = AutoField(primary_key=True)
    title = CharField(max_length=255, constraints=[Check("length(title) >=1 ")])
    discipline_id = IntegerField()
    file_path = CharField(max_length=500, null=True)
    file_name = CharField(max_length=255, null=True)
    version = CharField(max_length=20, constraints=[Check("length(version) >= 1")])
    approved_year = IntegerField(constraints=[Check('approved_year >= 2000')])
    description = CharField(max_length=1000, null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'work_programs'
        indexes = (
            (('discipline_id', 'version', 'approved_year'), True),
        )

    def save(self, *args, **kwargs):
        # updated_at обновляется только при изменении, не при создании
        if self._pk is not None:
            self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def soft_delete(cls, work_program_id):
        """Мягкое удаление: is_active = False.
        Возвращает True если деактивировано, иначе False."""
        updated = cls.update(is_active=False).where(
            (cls.id == work_program_id) & (cls.is_active == True)
        ).execute()
        return bool(updated > 0)

    def get_specialties(self):
        """Получить список ID специальностей привязанных к программе."""
        return list(
            WorkProgramSpecialty.select()
            .where(WorkProgramSpecialty.work_program == self)
        )


class WorkProgramSpecialty(BaseModel):
    """Транзитивная таблица: связь многие ко многим между WorkProgram и Specialty.
    specialty_id — внешний ID из Specialty Service, не хранится локально.
    Валидация существования specialty_id выполняется на уровне сервиса."""
    id = AutoField(primary_key=True)
    work_program = ForeignKeyField(WorkProgram, backref='wp_specialties', on_delete='CASCADE')
    specialty_id = IntegerField()

    class Meta:
        table_name = 'work_program_specialties'
        indexes = (
            (('work_program', 'specialty_id'), True),
        )

    @classmethod
    def attach(cls, work_program_id: int, specialty_id: int):
        """Привязать специальность к рабочей программе.
        Возвращает созданную запись."""
        return cls.create(
            work_program_id=work_program_id,
            specialty_id=specialty_id
        )

    @classmethod
    def detach(cls, record_id: int):
        """Отвязать специальность по ID записи о связи.
        Возвращает True если запись удалена, иначе False."""
        deleted = cls.delete().where(cls.id == record_id).execute()
        return bool(deleted > 0)

    @classmethod
    def get_by_program(cls, work_program_id: int):
        """Получить список специальностей рабочей программы по ID рабочей программы."""
        return list(
            cls.select().where(cls.work_program_id == work_program_id)
        )


def init_db():
    """Создание таблиц и заполнение начальными данными"""
    db.connect()
    db.create_tables([WorkProgram, WorkProgramSpecialty], safe=True)

    if not WorkProgram.select().exists():
        wp1 = WorkProgram.create(
            title='Рабочая программа по Математике',
            discipline_id=1,
            file_name='math_wp_v1.pdf',
            file_path='/programs/math_wp_v1.pdf',
            version='1.0',
            approved_year=2024,
            description='Рабочая программа дисциплины Математика для СПО'
        )
        wp2 = WorkProgram.create(
            title='Рабочая программа МДК 01.01',
            discipline_id=3,
            file_name='mdk0101_wp_v2.pdf',
            file_path='/programs/mdk0101_wp_v2.pdf',
            version='2.0',
            approved_year=2024
        )

        WorkProgramSpecialty.attach(wp1.id, 1)
        WorkProgramSpecialty.attach(wp1.id, 2)
        WorkProgramSpecialty.attach(wp2.id, 1)


if __name__ == '__main__':
    init_db()
    print("База данных work_program.db успешно инициализирована.")