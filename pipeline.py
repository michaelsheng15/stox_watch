from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

import time

from scripts.vantage_bal_shts import fetch_and_save_bal_sht
from scripts.vantage_cash_flow import fetch_and_save_cash_flow
from scripts.vantage_inc_stmts import fetch_and_save_income_statements
from scripts.vantage_top_glm import fetch_and_save_top_glm
from scripts.vantage_senti import fetch_and_save_sentiment

from scripts.yahoo_insider_purchases import main as fetch_and_save_insider_purchases
from scripts.yahoo_prices import main as fetch_and_save_ticker_prices
from scripts.yahoo_recommendations import main as fetch_and_save_recommendations

from scripts.yquery_earnings_trends import main as fetch_and_save_earnings_trends
from scripts.yquery_earnings import main as fetch_and_save_earnings
from scripts.yquery_financial_data import main as fetch_and_save_financial_data
from scripts.yquery_key_stats import main as fetch_and_save_key_stats
from scripts.yquery_summary_detail import main as fetch_and_save_summary_detail

from modelling.arima import main as forecast_prices
from modelling.covariance import main as calculate_covariance
from modelling.portfolio_optimization import main as register_recommendations

from utils.send_email import main as notification
import utils.monitoring_service as logging


def email_notifier(full_coverage=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            process_text = f"Starting {func.__name__}"
            status = "START"
            logging.log_monitor_to_sql(process_text, status)

            try:
                process_text = f"Running {func.__name__}"
                status = "FETCHING"
                logging.log_monitor_to_sql(process_text, status)

                result = func(*args, **kwargs)
                if full_coverage:
                    notification(
                        subject=f"Task {func.__name__} completed",
                        sentences=f"The task {func.__name__} has been completed successfully.",
                    )
                process_text = f"Completed {func.__name__}"
                status = "FINISH"
                logging.log_monitor_to_sql(process_text, status)
                return result
            except Exception as e:
                notification(
                    subject=f"Task {func.__name__} failed",
                    sentences=f"The task {func.__name__} failed with error: {e}",
                )
                process_text = f"Failed {func.__name__} with error: {e}"
                status = "ERROR"
                logging.log_monitor_to_sql(process_text, status)

                raise

        return wrapper

    return decorator


executors = {"default": ThreadPoolExecutor(10)}

job_defaults = {"max_instances": 5}

scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)


@email_notifier(full_coverage=False)
def balance_sheets():
    fetch_and_save_bal_sht()


@email_notifier(full_coverage=False)
def cash_flow():
    fetch_and_save_cash_flow()


@email_notifier(full_coverage=False)
def income_statements():
    fetch_and_save_income_statements()


@email_notifier(full_coverage=False)
def top_n_stats():
    fetch_and_save_top_glm()


@email_notifier(full_coverage=False)
def insider_purchases():
    fetch_and_save_insider_purchases()


@email_notifier(full_coverage=False)
def ticker_prices():
    fetch_and_save_ticker_prices()


@email_notifier(full_coverage=False)
def recs():
    fetch_and_save_recommendations()


@email_notifier(full_coverage=False)
def earnings_trends():
    fetch_and_save_earnings_trends()


@email_notifier(full_coverage=False)
def earnings():
    fetch_and_save_earnings()


@email_notifier(full_coverage=False)
def financial_data():
    fetch_and_save_financial_data()


@email_notifier(full_coverage=False)
def key_stats():
    fetch_and_save_key_stats()


@email_notifier(full_coverage=False)
def summary_detail():
    fetch_and_save_summary_detail()


@email_notifier(full_coverage=False)
def price_forecast():
    forecast_prices()


@email_notifier(full_coverage=False)
def covariance():
    calculate_covariance()


@email_notifier(full_coverage=False)
def optimize_portfolio():
    register_recommendations(save_df=True)


@email_notifier(full_coverage=False)
def sentiment():
    fetch_and_save_sentiment()


if __name__ == "__main__":

    scheduler.add_job

    scheduler.add_job(ticker_prices, "cron", hour=19, minute=10)
    scheduler.add_job(price_forecast, "cron", hour=19, minute=20)
    scheduler.add_job(covariance, "cron", hour=19, minute=30)

    scheduler.add_job(optimize_portfolio, "cron", hour=19, minute=40)

    scheduler.add_job(financial_data, "cron", hour=20, minute=0)
    scheduler.add_job(summary_detail, "cron", hour=20, minute=10)
    scheduler.add_job(recs, "cron", hour=20, minute=20)
    scheduler.add_job(top_n_stats, "cron", hour=20, minute=30)
    scheduler.add_job(insider_purchases, "cron", hour=20, minute=40)
    scheduler.add_job(income_statements, "cron", hour=20, minute=50)
    scheduler.add_job(earnings_trends, "cron", hour=21, minute=0)
    scheduler.add_job(earnings, "cron", hour=21, minute=10)
    scheduler.add_job(balance_sheets, "cron", hour=21, minute=20)
    scheduler.add_job(key_stats, "cron", hour=21, minute=30)
    scheduler.add_job(cash_flow, "cron", hour=21, minute=40)
    scheduler.add_job(sentiment, "cron", hour=21, minute=50)

    scheduler.start()
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
