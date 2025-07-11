from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, CartItem 
from django.http import JsonResponse
from .models import Product

def product_list(request):
    """
    Displays a list of all available products.
    """
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    """
    Displays the details of a single product.
    """
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

def add_to_cart(request, pk):
    """
    Adds a specified product to the user's session-based shopping cart.
    If the product is already in the cart, its quantity is increased.
    """
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {}) 
    product_id_str = str(product.id) 

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price), 
            'quantity': 1,
            'image_url': product.image_url,
        }

    request.session['cart'] = cart 
    request.session.modified = True 

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': f'{product.name} added to cart!'})
    else:
        return redirect('view_cart')

def view_cart(request):
    """
    Displays the contents of the user's session-based shopping cart.
    Calculates the total price of items in the cart.
    """
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, item_data in cart.items():
        item_price = float(item_data['price']) * item_data['quantity']
        total_price += item_price
        cart_items.append({
            'product_id': product_id,
            'name': item_data['name'],
            'price': float(item_data['price']),
            'quantity': item_data['quantity'],
            'image_url': item_data.get('image_url', ''),
            'subtotal': item_price,
        })

    return render(request, 'products/cart.html', {'cart_items': cart_items, 'total_price': total_price})



def update_cart_quantity(request, product_id):
    """Handle quantity updates via AJAX"""
    if not request.method == 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str not in cart:
        return JsonResponse({'status': 'error', 'message': 'Product not in cart'}, status=404)

    action = request.POST.get('action')
    
    if action == 'increase':
        cart[product_id_str]['quantity'] += 1
    elif action == 'decrease':
        if cart[product_id_str]['quantity'] > 1:
            cart[product_id_str]['quantity'] -= 1
        else:
            del cart[product_id_str]
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({
                'status': 'success',
                'new_quantity': 0,
                'total_price': sum(float(item['price']) * item['quantity'] for item in cart.values())
            })
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    request.session['cart'] = cart
    request.session.modified = True
    
    new_quantity = cart[product_id_str]['quantity']
    new_subtotal = float(cart[product_id_str]['price']) * new_quantity
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'status': 'success',
        'new_quantity': new_quantity,
        'new_subtotal': new_subtotal,
        'total_price': total_price
    })

def remove_from_cart(request, product_id):
    """Handle item removal via AJAX"""
    if not request.method == 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str not in cart:
        return JsonResponse({'status': 'error', 'message': 'Product not in cart'}, status=404)

    # Remove the item from cart
    del cart[product_id_str]
    request.session['cart'] = cart
    request.session.modified = True
    
    # Calculate new total
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'status': 'success',
        'total_price': total_price
    })