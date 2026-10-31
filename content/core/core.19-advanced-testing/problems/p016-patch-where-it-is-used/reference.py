def targets():
    return {
        "greeting": "app_greet.now",
        "stamp": "clock.now",
        "has_config": "app_files.exists",
        "welcome": "app_mail.Mailer",
    }
