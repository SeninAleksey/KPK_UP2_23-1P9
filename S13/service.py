from models import WorkProgram, Discipline, Specialty, database


def get_work_program(work_program_id: int):
    """Получить рабочую программу по ID."""
    return WorkProgram.get_or_none(WorkProgram.id == work_program_id)


def create_work_program(discipline_id: int, specialty_id: int, file_url: str,
                        file_name: str, file_size: int = 0, version: str = "1.0",
                        approved_by: str = None, approval_date=None, description: str = ""):
    """Добавить рабочую программу. Возвращает объект WorkProgram или None при ошибке."""
    if not WorkProgram.validate_url(file_url):
        return None
    if not WorkProgram.validate_version(version):
        return None
    try:
        return WorkProgram.create(
            discipline_id=discipline_id,
            specialty_id=specialty_id,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            version=version,
            approved_by=approved_by,
            approval_date=approval_date,
            description=description,
        )
    except Exception:
        return None


def update_work_program(work_program_id: int, **fields):
    """Изменить рабочую программу по ID. Возвращает объект WorkProgram или None."""
    wp = WorkProgram.get_or_none(WorkProgram.id == work_program_id)
    if wp is None:
        return None
    allowed = {'file_url', 'file_name', 'file_size', 'version',
               'approved_by', 'approval_date', 'description', 'is_active'}
    for key, value in fields.items():
        if key not in allowed:
            continue
        if key == 'file_url' and not WorkProgram.validate_url(value):
            return None
        if key == 'version' and not WorkProgram.validate_version(value):
            return None
        setattr(wp, key, value)
    wp.save()
    return wp


def delete_work_program(work_program_id: int) -> bool:
    """Мягкое удаление рабочей программы. Возвращает True/False."""
    return WorkProgram.soft_delete(work_program_id)


def list_work_programs(discipline_id=None, specialty_id=None, version=None,
                       is_active=None, approved_by=None, limit=100, offset=0):
    """Получить список рабочих программ с фильтрацией."""
    return WorkProgram.get_list(
        discipline_id=discipline_id,
        specialty_id=specialty_id,
        version=version,
        is_active=is_active,
        approved_by=approved_by,
        limit=limit,
        offset=offset,
    )
