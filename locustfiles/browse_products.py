from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):

    wait_time = between(1, 5)

    # task decorator takes priority of how much user can do this task.

    @task(3)
    def view_products(self):
        user_id = randint(1, 500)
        self.client.get(
            f'/invoicing/products/?user_id={user_id}',
            name='/invoicing/products'
        )

    @task(1)
    def view_product(self):
        product_id = randint(1, 100)
        self.client.get(
            f'/invoicing/products/{product_id}',
            name='/invoicing/products/:id'
        )
