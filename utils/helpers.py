from datetime import datetime, timedelta
from models.worker_model import WorkerModel
from models.availability_model import AvailabilityModel
from models.days_off_model import DaysOffModel
from models.seasonal_schedule_model import SeasonalScheduleModel
from models.detail_model import DetailModel
from models.appointment_model import AppointmentModel

def check_availability(worker, worker_id, service_id, date, time, schedule, current_appointment_id=None):
    # Check if the service duration fits within the available time slot
    detail = DetailModel.query.filter_by(site_id=worker.site_id, service_id=service_id).first()
    if detail:
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
                right_overlapping_detail = DetailModel.query.filter_by(site_id=right_overlapping_appointment.site_id, service_id=right_overlapping_appointment.service_id).first()
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
                left_overlapping_detail = DetailModel.query.filter_by(site_id=left_overlapping_appointment.site_id, service_id=left_overlapping_appointment.service_id).first()
                if left_overlapping_detail:
                    left_overlapping_start_time = left_overlapping_appointment.appointmenttime.time()
                    if left_overlapping_start_time < end_time:
                        return False, "Worker has an overlapping appointment"
            return True, "Worker is available"
        else:
            return False, "Worker is not available for the full duration of the service"

def is_worker_available(worker_id, date, time, service_id, current_appointment_id=None):
    # Check if the worker is active
    worker = WorkerModel.query.filter_by(id=worker_id, active=True).first()
    if not worker:
        return False, "Worker not found or inactive"

    # Check if the worker has a day off
    dayoff = DaysOffModel.query.filter_by(worker_id=worker_id, dayoff=date).first()
    if dayoff:
        return False, "Worker is not available on this day"

    # Check if the worker has a seasonal schedule
    seasonal_schedule = SeasonalScheduleModel.query.filter(
        SeasonalScheduleModel.worker_id == worker_id,
        SeasonalScheduleModel.startdate <= date,
        SeasonalScheduleModel.enddate >= date
    ).first()
    if seasonal_schedule:
        if seasonal_schedule.starttime <= time <= seasonal_schedule.endtime:
            return check_availability(worker, worker_id, service_id, date, time, seasonal_schedule, current_appointment_id)
        else:
            return False, "Worker is not available at this time"

    # Check the worker's regular availability
    weekday = date.strftime('%A')
    availability = AvailabilityModel.query.filter_by(worker_id=worker_id, weekday=weekday).all()
    for slot in availability:
        if slot.starttime <= time <= slot.endtime:
            return check_availability(worker, worker_id, service_id, date, time, slot, current_appointment_id)
        else:
            return False, "Worker is not available at this time"