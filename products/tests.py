import pytest
from django.urls import reverse
from products.models import Product

@pytest.fixture
def product_fixture():
    """
    Fixture to create a single product instance for tests.
    """
    return Product.objects.create(
        name="Test Product",
        description="This is a test product description.",
        price=19.99,
        image_url="http://example.com/test_image.jpg"
    )


@pytest.fixture
def multiple_products_fixture():
    """
    Fixture to create multiple product instances for tests.
    """
    product_a = Product.objects.create(
        name="Product A",
        description="Description A",
        price=10.00
    )
    product_b = Product.objects.create(
        name="Product B",
        description="Description B",
        price=20.00
    )
    return product_a, product_b

@pytest.fixture
def client():
    """
    Fixture for Django's test client.
    """
    from django.test import Client
    return Client()


@pytest.mark.django_db #
def test_product_creation(product_fixture):
    """
    Verify that a product can be created successfully.
    """
    assert product_fixture.name == "Test Product"
    assert product_fixture.description == "This is a test product description."
    assert product_fixture.price == 19.99
    assert product_fixture.image_url == "http://example.com/test_image.jpg"
    assert isinstance(product_fixture, Product)

@pytest.mark.django_db
def test_product_str_representation(product_fixture):
    """
    Verify the __str__ method of the Product model.
    """
    assert str(product_fixture) == "Test Product"

@pytest.mark.django_db
def test_product_list_view(client, multiple_products_fixture):
    """
    Test the product list.
    """
    product_a, product_b = multiple_products_fixture
    response = client.get(reverse('product_list'))
    assert response.status_code == 200
    assert f'<h2 class="text-3xl font-bold mb-6 text-center text-gray-800">Our Products</h2>' in response.content.decode('utf-8')
    assert product_a.name in response.content.decode('utf-8')
    assert product_b.name in response.content.decode('utf-8')
    assert 'products' in response.context
    assert len(response.context['products']) == 2

@pytest.mark.django_db
def test_product_detail_view(client, product_fixture):
    """
    Test the product detail view.
    """
    response = client.get(reverse('product_detail', args=[product_fixture.pk]))
    assert response.status_code == 200
    assert product_fixture.name in response.content.decode('utf-8')
    assert str(product_fixture.price) in response.content.decode('utf-8')
    assert product_fixture.description in response.content.decode('utf-8')
    assert 'product' in response.context
    assert response.context['product'] == product_fixture

@pytest.mark.django_db
def test_add_to_cart_view(client, product_fixture):
    """
    Test the add_to_cart function.
    """
    response = client.post(reverse('add_to_cart', args=[product_fixture.pk]), follow=True)
    assert response.status_code == 200 
    assert response.redirect_chain[0][0] == reverse('view_cart')
    assert response.redirect_chain[0][1] == 302 
   
    assert 'cart' in client.session
    cart = client.session['cart']
    assert str(product_fixture.id) in cart
    assert cart[str(product_fixture.id)]['quantity'] == 1

    response = client.post(reverse('add_to_cart', args=[product_fixture.pk]), follow=True)
    assert response.status_code == 200
    cart = client.session['cart']
    assert cart[str(product_fixture.id)]['quantity'] == 2 

@pytest.mark.django_db
def test_view_cart_view(client, multiple_products_fixture):
    """
    Test the view_cart view to ensure it displays cart contents and total.
    """
    product_a, product_b = multiple_products_fixture
    client.post(reverse('add_to_cart', args=[product_a.pk]))
    client.post(reverse('add_to_cart', args=[product_b.pk]))

    response = client.get(reverse('view_cart'))
    assert response.status_code == 200
    assert 'cart_items' in response.context
    assert 'total_price' in response.context

    cart_items = response.context['cart_items']
    total_price = response.context['total_price']

    assert len(cart_items) == 2
    assert product_a.name in response.content.decode('utf-8')
    assert product_b.name in response.content.decode('utf-8')

    expected_total = float(product_a.price) + float(product_b.price)
    assert total_price == pytest.approx(expected_total) 

@pytest.mark.django_db
def test_view_cart_empty(client):
    """
    Test the view_cart view when the cart is empty.
    """
    response = client.get(reverse('view_cart'))
    assert response.status_code == 200
    assert "Your cart is empty." in response.content.decode('utf-8')
    assert len(response.context['cart_items']) == 0
    assert response.context['total_price'] == 0

@pytest.mark.django_db
def test_update_cart_quantity_increase(client, product_fixture):
    """
    Test increasing product quantity in the cart.
    """
    client.post(reverse('add_to_cart', args=[product_fixture.pk]))
    cart = client.session['cart']
    assert cart[str(product_fixture.id)]['quantity'] == 1

    response = client.post(reverse('update_cart_quantity', args=[product_fixture.pk]), {'action': 'increase'})
    assert response.status_code == 200
    json_response = response.json()
    assert json_response['status'] == 'success'
    assert json_response['new_quantity'] == 2
    assert client.session['cart'][str(product_fixture.id)]['quantity'] == 2
    assert json_response['total_price'] == pytest.approx(float(product_fixture.price) * 2)

@pytest.mark.django_db
def test_update_cart_quantity_decrease(client, product_fixture):
    """
    Test decreasing product quantity in the cart.
    """
    client.post(reverse('add_to_cart', args=[product_fixture.pk]))
    client.post(reverse('add_to_cart', args=[product_fixture.pk]))
    cart = client.session['cart']
    assert cart[str(product_fixture.id)]['quantity'] == 2

    response = client.post(reverse('update_cart_quantity', args=[product_fixture.pk]), {'action': 'decrease'})
    assert response.status_code == 200
    json_response = response.json()
    assert json_response['status'] == 'success'
    assert json_response['new_quantity'] == 1
    assert client.session['cart'][str(product_fixture.id)]['quantity'] == 1
    assert json_response['total_price'] == pytest.approx(float(product_fixture.price) * 1)

@pytest.mark.django_db
def test_update_cart_quantity_decrease_to_zero_removes_item(client, product_fixture):
    """
    Test decreasing product quantity to zero removes it from the cart.
    """
    client.post(reverse('add_to_cart', args=[product_fixture.pk]))
    cart = client.session['cart']
    assert cart[str(product_fixture.id)]['quantity'] == 1

    response = client.post(reverse('update_cart_quantity', args=[product_fixture.pk]), {'action': 'decrease'})
    assert response.status_code == 200
    json_response = response.json()
    assert json_response['status'] == 'success'
    assert json_response['new_quantity'] == 0 
    assert str(product_fixture.id) not in client.session['cart']
    assert json_response['total_price'] == 0.0

@pytest.mark.django_db
def test_remove_from_cart_view(client, product_fixture):
    """
    Test removing a product entirely from the cart.
    """
    client.post(reverse('add_to_cart', args=[product_fixture.pk]))
    assert str(product_fixture.id) in client.session['cart']

    response = client.post(reverse('remove_from_cart', args=[product_fixture.pk]))
    assert response.status_code == 200
    json_response = response.json()
    assert json_response['status'] == 'success'
    assert str(product_fixture.id) not in client.session['cart']
    assert json_response['total_price'] == 0.0

@pytest.mark.django_db
def test_remove_from_cart_non_existent_item(client):
    """Test removing an item that doesn't exist in cart"""
    response = client.post(reverse('remove_from_cart', args=[999]))
    assert response.status_code == 404
    json_response = response.json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Product not in cart'
