# E-commerce Demo 🛍️ ![Django CI](https://github.com/jinitha01/ecom-demo/workflows/Django%20CI/badge.svg)

This is a basic e-commerce web application built with **Django**, showcasing essential features like product listing, a dynamic session-based shopping cart, and robust automated testing. It's set up with a **GitHub Actions CI/CD pipeline** for continuous quality assurance, ensuring code reliability and smooth deployments.

---

## ✨ Features

* **Product Listing**: Browse through a variety of products with ease.
* **Product Detail**: View detailed information for each product, including descriptions and images.
* **Dynamic Shopping Cart**:
    * Add products to your cart directly from the product list or detail pages.
    * Increase or decrease product quantities in your cart.
    * Remove items from your cart.
* **Automated Testing with Pytest**: Comprehensive tests ensure the application's stability and correct functionality.
* **Continuous Integration/Continuous Deployment (CI/CD)**: Automated workflows with GitHub Actions guarantee code quality and streamline deployment.

---

## 🚀 Tech Stack

| Category     | Technologies                                      |
| :----------- | :------------------------------------------------ |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white) ![Jinja2](https://img.shields.io/badge/Jinja2-white?style=for-the-badge&logo=jinja&logoColor=black) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white) |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white) |
| **CI/CD** | ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white) |

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

* **Python**: Version 3.8 or higher.
* **pip**: Python package installer.
* **Git**: Required for cloning repository and automated build and test in github actions

---

## ⚙️ Setup Instructions

Follow these steps to get your development environment up and running:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/jinitha01/ecom-demo.git](https://github.com/jinitha01/ecom-demo.git)
    cd ecom_demo
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Django and other dependencies:**
    First, create a `requirements.txt` file in your `ecom_demo` directory with the following content:
    ```
    Django==5.2.4
    pytest==8.4.1
    pytest-django==4.11.1
    requests==2.32.4
    webdriver-manager==4.0.2
    selenium==4.34.2
    ```
    Then, install them:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Start a Django project:**
    *(Note: This step is typically done once to initialize the project structure. If the `ecom_demo` project directory already exists with its files, you can skip this.)*
    ```bash
    django-admin startproject ecom_demo .
    ```

6.  **Create a Django app:**
    ```bash
    python manage.py startapp products
    ```

7.  **Make migrations:**
    This command creates new migration files based on changes detected in your models.
    ```bash
    python manage.py makemigrations products
    ```

8.  **Initialize the database:**
    This command applies the migrations to your database, creating or updating tables.
    ```bash
    python manage.py migrate
    ```

9.  **Create an admin user (optional, but recommended for accessing Django admin):**
    ```bash
    python manage.py createsuperuser
    ```

10. **Launch the development server:**
    ```bash
    python manage.py runserver
    ```
    Access the application in your web browser at: 👉 [http://localhost:8000](http://localhost:8000)

---

## Screenshots

![Homepage with product listings](https://github.com/jinitha01/ecom-demo/raw/readme/screenshots/1.png)
*Description of Screenshot 1: Homepage with product listings.*

![Shopping cart view](https://github.com/jinitha01/ecom-demo/raw/readme/screenshots/3.png)
*Description of Screenshot 2: Product details view.*

![Shopping cart view](https://github.com/jinitha01/ecom-demo/raw/readme/screenshots/2.png)
*Description of Screenshot 3: Empty Shopping cart view.*

![Shopping cart view](https://github.com/jinitha01/ecom-demo/raw/readme/screenshots/4.png)
*Description of Screenshot 4: Shopping cart view with one product.*

![Shopping cart view](https://github.com/jinitha01/ecom-demo/raw/readme/screenshots/5.png)
*Description of Screenshot 5: Shopping cart view with multiple products.*

## 🚀 CI/CD Pipeline

This project leverages GitHub Actions for continuous integration and deployment, ensuring that every push and pull request to the `main` branch is automatically tested. The workflow is defined in `.github/workflows/django_ci.yml`.

### Workflow Details (`django_ci.yml`)

The CI/CD pipeline consists of two main jobs: `build_unit_tests` and `e2e_tests`.

* **`build_unit_tests`**:
    * Runs on `ubuntu-latest`.
    * Sets up Python 3.12.
    * Installs project dependencies from `requirements.txt`, along with `pytest` and `pytest-django`.
    * Runs database migrations.
    * Executes unit tests located in `products/tests.py`.

* **`e2e_tests`**:
    * Depends on `build_unit_tests` to ensure unit tests pass first.
    * Runs on `ubuntu-latest`.
    * Sets up Python 3.12.
    * Installs project dependencies, `selenium`, and `pytest-selenium`.
    * Installs `chromium-browser` and `chromium-chromedriver` for headless browser testing.
    * Runs database migrations.
    * Starts the Django development server in the background.
    * Executes end-to-end tests located in `ecom_demo/e2e_tests/`.
    * Gracefully stops the Django server.
    * Uploads screenshots of failed E2E tests as an artifact for debugging.

### Environment Variables

The workflow uses several environment variables:

* `DJANGO_SETTINGS_MODULE`: Specifies the Django settings file.
* `PYTHONUNBUFFERED`: Ensures Python output is unbuffered, useful for logging.
* `SECRET_KEY`: Retrieves the Django secret key from GitHub Secrets (`secrets.DJANGO_SECRET_KEY`). **Ensure this secret is configured in your GitHub repository settings.**
* `DEBUG`: Set to `'False'` for production-like testing environments.
* `ALLOWED_HOSTS`: Specifies allowed hosts for the Django application.

---

## 📂 Project Structure

```
ecom-demo/
├── .github/
│   └── workflows/
│       └── django_ci.yml
├── ecom_demo/
│   ├── e2e_tests/
│   │   └── test_ecom.py
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/
│   ├── templates/
│   │   └── products/
│   │       ├── base.html
│   │       ├── cart.html
│   │       ├── product_detail.html
│   │       └── product_list.html
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── urls.py
│   └── views.py
├── manage.py
├── pytest.ini
└── requirements.txt