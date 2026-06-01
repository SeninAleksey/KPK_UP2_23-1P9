from datetime import datetime
from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, BooleanField, Check, TextField
)

db = SqliteDatabase('work_program.db')


class BaseModel(Model):
    class Meta:
        database = db


class Discipline(BaseModel):
    """Внешняя сущность: дисциплина (заглушка, управляется Discipline Service)"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True)

    class Meta:
        table_name = 'disciplines'


class Specialty(BaseModel):
    """Внешняя сущность: специальность (заглушка, управляется Specialty Service)"""
    id = AutoField(primary_key=True)
    code = CharField(max_length=20, unique=True)
    name = CharField(max_length=200)

    class Meta:
        table_name = 'specialties'


class WorkProgram(BaseModel):
    """Основная сущность: рабочая программа дисциплины"""
    id = AutoField(primary_key=True)
    title = CharField(max_length=255, constraints=[Check("length(title) >= 1")])
    discipline = ForeignKeyField(Discipline, backref='work_programs', on_delete='RESTRICT')
    file_path = CharField(max_length=500, null=True)
    file_name = CharField(max_length=255, null=True)
    version = CharField(max_length=20, constraints=[Check("length(version) >= 1")])
    approved_year = IntegerField(constraints=[Check('approved_year >= 2000')])
    description = TextField(null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'work_programs'
        indexes = (
            # одна дисциплина — одна версия программы (уникальная комбинация)
            (('discipline', 'version', 'approved_year'), True),
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


class WorkProgramSpecialty(BaseModel):
    """Транзитивная таблица: рабочая программа может применяться
    в нескольких специальностях, специальность может иметь
    несколько рабочих программ (многие ко многим)"""
    id = AutoField(primary_key=True)
    work_program = ForeignKeyField(WorkProgram, backref='wp_specialties', on_delete='CASCADE')
    specialty = ForeignKeyField(Specialty, backref='wp_specialties', on_delete='RESTRICT')

    class Meta:
        table_name = 'work_program_specialties'
        indexes = (
            (('work_program', 'specialty'), True),  # каждая пара уникальна
        )


def init_db():
    """Создание таблиц и заполнение начальными данными"""
    db.connect()
    db.create_tables([Discipline, Specialty, WorkProgram, WorkProgramSpecialty], safe=True)

    if not Discipline.select().exists():
        d1 = Discipline.create(name='Математика')
        d2 = Discipline.create(name='Физика')
        d3 = Discipline.create(name='МДК 01.01 Разработка программных модулей')

        sp1 = Specialty.create(code='09.02.07', name='Информационные системы и программирование')
        sp2 = Specialty.create(code='09.02.06', name='Сетевое и системное администрирование')

        wp1 = WorkProgram.create(
            title='Рабочая программа по Математике',
            discipline=d1,
            file_name='math_wp_v1.pdf',
            file_path='/programs/math_wp_v1.pdf',
            version='1.0',
            approved_year=2024,
            description='Рабочая программа дисциплины Математика для СПО'
        )
        wp2 = WorkProgram.create(
            title='Рабочая программа МДК 01.01',
            discipline=d3,
            file_name='mdk0101_wp_v2.pdf',
            file_path='/programs/mdk0101_wp_v2.pdf',
            version='2.0',
            approved_year=2024
        )

        WorkProgramSpecialty.create(work_program=wp1, specialty=sp1)
        WorkProgramSpecialty.create(work_program=wp1, specialty=sp2)
        WorkProgramSpecialty.create(work_program=wp2, specialty=sp1)


if __name__ == '__main__':
    init_db()
    print("База данных work_program.db успешно инициализирована.")
