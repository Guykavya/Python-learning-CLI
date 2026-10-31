def targets():
    return {
        "greeting": "clock.now",
        "stamp": "clock.now",
        "has_config": "os.path.exists",
        "welcome": "mailer.Mailer",
    }
