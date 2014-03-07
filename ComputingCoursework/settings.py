import os;
BASE_DIR = os.path.dirname(os.path.dirname(__file__));
SETTINGS_DIR = os.path.dirname(__file__);
PROJECT_PATH = os.path.abspath(os.path.join(SETTINGS_DIR, os.pardir));



SECRET_KEY = "7ts7^z300)r$-m8p3=^oq+65=nyrl3h*&)i9&*&%oylevnx&z("''

DEBUG = True;

TEMPLATE_DEBUG = True;

ALLOWED_HOSTS = ["localhost", "127.0.0.1"];



INSTALLED_APPS = (
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"django.contrib.webdesign",
	"socialsite"
);

MIDDLEWARE_CLASSES = (
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware"
);



ROOT_URLCONF = "ComputingCoursework.urls";

WSGI_APPLICATION = "ComputingCoursework.wsgi.application";



DATABASE_PATH = os.path.join(PROJECT_PATH, "social_site.db");

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.sqlite3",
		"NAME": DATABASE_PATH
	}
};



LANGUAGE_CODE = "en-uk";

TIME_ZONE = "UTC";

USE_I18N = True;

USE_L10N = True;

USE_TZ = True;



STATIC_PATH = os.path.join(PROJECT_PATH, "static");
STATIC_URL = "/static/";
STATICFILES_DIRS = (
	STATIC_PATH,
);


TEMPLATE_PATH = os.path.join(PROJECT_PATH, "templates");
TEMPLATE_DIRS = (
	TEMPLATE_PATH,
);


MEDIA_URL = "/media/";
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media");


LOGIN_URL = "/";