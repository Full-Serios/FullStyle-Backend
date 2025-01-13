from datetime import datetime, timedelta
from models.worker_model import WorkerModel
from models.availability_model import AvailabilityModel
from models.days_off_model import DaysOffModel
from models.seasonal_schedule_model import SeasonalScheduleModel
from models.detail_model import DetailModel
from models.appointment_model import AppointmentModel
from models.service_model import ServiceModel
from models.category_model import CategoryModel
from models.site_model import SiteModel
from models.category_model import CategoryModel
from models.site_has_category_model import SiteHasCategoryModel
from models.worker_has_service_model import WorkerHasServiceModel

#
#   Helpers for appointment
#

def check_worker_exists(worker_id):
    worker = WorkerModel.query.filter_by(id=worker_id).first()
    if not worker:
        return None, "Worker not found"
    return worker, None

def check_worker_active(worker_id):
    worker = WorkerModel.query.filter_by(id=worker_id, active=True).first()
    if not worker:
        return None, "Worker not found or inactive"
    return worker, None

def check_appointment_time(appointment_time_str):
    try:
        date = datetime.strptime(appointment_time_str, '%Y-%m-%dT%H:%M:%S')
        return date, None
    except ValueError:
        return None, "Invalid date format. Use 'YYYY-MM-DDTHH:MM:SS'."

def check_worker_day_off(worker_id, date):
    dayoff = DaysOffModel.query.filter_by(worker_id=worker_id, dayoff=date).first()
    if dayoff:
        return False, "Worker is not available on this day"
    return True, None

def check_seasonal_schedule(worker_id, date, time):
    seasonal_schedule = SeasonalScheduleModel.query.filter(
        SeasonalScheduleModel.worker_id == worker_id,
        SeasonalScheduleModel.startdate <= date,
        SeasonalScheduleModel.enddate >= date
    ).first()
    if seasonal_schedule:
        if seasonal_schedule.starttime <= time <= seasonal_schedule.endtime:
            return seasonal_schedule, None
        else:
            return None, "Worker is not available at this time"
    return None, None

def check_regular_availability(worker_id, date, time):
    weekday = date.strftime('%A')
    availability = AvailabilityModel.query.filter_by(worker_id=worker_id, weekday=weekday).all()
    for slot in availability:
        if slot.starttime <= time <= slot.endtime:
            return slot, None
    return None, "Worker is not available at this time"

def check_service_detail(worker, service_id):
    detail = DetailModel.query.filter_by(site_id=worker.site_id, service_id=service_id).first()
    if not detail:
        return None, "Service detail not found"
    return detail, None

def check_appointment_exists(appointment_id):
    appointment = AppointmentModel.find_by_id(appointment_id)
    if not appointment:
        return None, "Appointment not found"
    return appointment, None

#
#   Helpers for availability
#

def check_availability_exists(availability_id):
    availability = AvailabilityModel.query.filter_by(id=availability_id).first()
    if not availability:
        return None, "Availability not found"
    return availability, None

# Have to check if it doesn't conflict with updating the same register of availability 
def check_overlapping_availability(worker_id, weekday, starttime, endtime, current_availability_id=None):
    overlapping_availability = AvailabilityModel.query.filter(
        AvailabilityModel.worker_id == worker_id,
        AvailabilityModel.weekday == weekday,
        AvailabilityModel.starttime < endtime,
        AvailabilityModel.endtime > starttime,
        AvailabilityModel.id != current_availability_id
    ).first()
    if overlapping_availability:
        return False, f"Overlapping availability found id={overlapping_availability.id}"
    return True, None

#
#   Helpers for days off
#

def check_date(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return date, None
    except ValueError:
        return None, "Invalid date format. Use 'YYYY-MM-DD'."

def check_dayoff_exists(dayoff_id):
    dayoff = DaysOffModel.query.filter_by(id=dayoff_id).first()
    if not dayoff:
        return None, "Day off not found"
    return dayoff, None

#
#   Helpers for detail
#

def check_detail_exists(site_id, service_id):
    detail = DetailModel.query.filter_by(site_id=site_id, service_id=service_id).first()
    if not detail:
        return None, "Detail not found"
    return detail, None

def check_detail_active(site_id, service_id):
    detail = DetailModel.query.filter_by(site_id=site_id, service_id=service_id, active=True).first()
    if not detail:
        return None, "Detail not found or inactive"
    return detail, None

def check_price(price):
    if not isinstance(price, int) or price < 0:
        return False, "Invalid price. Price must be a non-negative integer."
    return True, None

def check_duration(duration):
    if not isinstance(duration, int) or duration <= 0:
        return False, "Invalid duration. Duration must be a positive integer."
    return True, None

#
#   Helpers for seasonal_schedule
#

def check_time(time_str):
    try:
        time = datetime.strptime(time_str, '%H:%M:%S').time()
        return time, None
    except ValueError:
        return None, "Invalid time format. Use 'HH:MM:SS'."

def check_seasonal_schedule_exists(seasonal_schedule_id):
    seasonal_schedule = SeasonalScheduleModel.query.filter_by(id=seasonal_schedule_id).first()
    if not seasonal_schedule:
        return None, "Seasonal schedule not found"
    return seasonal_schedule, None

#
#   Helpers for service
#

def check_category_exists(category_id):
    category = CategoryModel.query.filter_by(id=category_id).first()
    if not category:
        return None, "Category not found"
    return category, None

def check_service_unique(name, category_id):
    service = ServiceModel.query.filter_by(name=name, category_id=category_id).first()
    if service:
        return False, "Service with the same name and category already exists"
    return True, None

#
#   Helpers for site_has_service
#

def check_site_exists(site_id):
    site = SiteModel.query.filter_by(id=site_id).first()
    if not site:
        return None, "Site not found"
    return site, None

def check_site_category_exists(site_id, category_id):
    site_category = SiteHasCategoryModel.query.filter_by(site_id=site_id, category_id=category_id).first()
    if site_category:
        return False, "Site-Category relationship already exists"
    return True, None

#
#   Helpers for site
#

def check_manager_exists(manager_id):
    manager = WorkerModel.query.filter_by(id=manager_id).first()
    if not manager:
        return None, "Manager not found"
    return manager, None

def check_phone(phone):
    if not isinstance(phone, int) or phone <= 0:
        return False, "Invalid phone number. Phone number must be a positive integer."
    return True, None

#
#   Helpers for worker_has_service
#

def check_service_allowed_for_site(site_id, service_id):
    site_service = DetailModel.query.filter_by(site_id=site_id, service_id=service_id).first()
    if not site_service:
        return False, "Service not allowed for this worker's site"
    return True, None

def check_worker_service_exists(worker_id, service_id):
    worker_service = WorkerHasServiceModel.query.filter_by(worker_id=worker_id, service_id=service_id).first()
    if worker_service:
        return False, "Worker-Service relationship already exists"
    return True, None

#
#   Helpers for worker
#

def check_overlapping_appointments(worker, worker_id, service_id, date, time, schedule, current_appointment_id=None):
    detail, error = check_service_detail(worker, service_id)
    if error:
        return False, error

    # Check if the service duration fits within the available time slot
    end_time = (datetime.combine(date, time) + timedelta(minutes=detail.duration)).time()
    if end_time <= schedule.endtime:
        # Check for overlapping appointments
        # Right overlapping appointment (before)
        right_overlapping_appointment = AppointmentModel.query.filter(
            AppointmentModel.worker_id == worker_id,
            AppointmentModel.appointmenttime <= datetime.combine(date, time),
            AppointmentModel.id != current_appointment_id
        ).order_by(AppointmentModel.appointmenttime.desc()).first()
        if right_overlapping_appointment:
            right_overlapping_detail, error = check_service_detail(right_overlapping_appointment, right_overlapping_appointment.service_id)
            if right_overlapping_detail:
                right_overlapping_end_time = (right_overlapping_appointment.appointmenttime + timedelta(minutes=right_overlapping_detail.duration)).time()
                if right_overlapping_end_time > time:
                    return False, "Worker has an overlapping appointment"
        # Left overlapping appointment (after)
        left_overlapping_appointment = AppointmentModel.query.filter(
            AppointmentModel.worker_id == worker_id,
            AppointmentModel.appointmenttime >= datetime.combine(date, time),
            AppointmentModel.id != current_appointment_id
        ).order_by(AppointmentModel.appointmenttime.asc()).first()
        if left_overlapping_appointment:
            left_overlapping_detail, error = check_service_detail(left_overlapping_appointment, left_overlapping_appointment.service_id)
            if left_overlapping_detail:
                left_overlapping_start_time = left_overlapping_appointment.appointmenttime.time()
                if left_overlapping_start_time < end_time:
                    return False, "Worker has an overlapping appointment"
        return True, "Worker is available"
    else:
        return False, "Worker is not available for the full duration of the service"
    
def is_worker_available(worker_id, date, time, service_id, current_appointment_id=None):
    # Check if the worker is active
    worker, error = check_worker_active(worker_id)
    if error:
        return False, error

    # Check if the worker has a day off
    available, error = check_worker_day_off(worker_id, date)
    if not available:
        return False, error

    # Check if the worker has a seasonal schedule
    seasonal_schedule, error = check_seasonal_schedule(worker_id, date, time)
    if seasonal_schedule:
        return check_overlapping_appointments(worker, worker_id, service_id, date, time, seasonal_schedule, current_appointment_id)
    elif error:
        return False, error

    # Check the worker's regular availability
    slot, error = check_regular_availability(worker_id, date, time)
    if slot:
        return check_overlapping_appointments(worker, worker_id, service_id, date, time, slot, current_appointment_id)
    else:
        return False, error