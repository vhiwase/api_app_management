from flask import Flask, request, jsonify
import redis

app = Flask(__name__)
redis_client = redis.StrictRedis(host='local_redis', port=6379, db=0)

# Endpoint to create an API product
@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    # Save product data in Redis hash
    redis_client.hset('products', product_id, product_name)
    return jsonify({
        'message': 'Product created successfully',
        'product_id': product_id,
        'product_name': product_name
    })

# Endpoint to add APIs to a product
@app.route('/api/products/<product_id>/apis', methods=['POST'])
def add_api_to_product(product_id):
    product_name = product_id and redis_client.hget('products', product_id)
    product_name = product_name and product_name.decode('utf-8')
    if product_name is None:
        return jsonify({'message': 'Product is not added'}), 403
    data = request.get_json()
    api_id = data.get('api_id')
    api_details = data.get('api_details')
    # Save API data in Redis hash with product_id as the hash name
    redis_client.hset(product_id, api_id, api_details)
    return jsonify({
        'message': 'API added to product successfully',
        "product_id": product_id,
        "api_id": api_id,
        "api_details": api_details
    })

# Endpoint to subscribe to a product
@app.route('/api/subscribe/<product_id>/users', methods=['POST'])
def subscribe_to_product(product_id):
    product_name = product_id and redis_client.hget('products', product_id)
    product_name = product_name and product_name.decode('utf-8')
    if product_name is None:
        return jsonify({'message': 'Product is not added'}), 403
    # Save subscription details in Redis set with user_id as a member
    data = request.get_json()
    user_id = data.get('user_id')
    redis_client.sadd(f'subscriptions:{user_id}', product_id)
    return jsonify({
        'message': 'User subscribed to the product successfully',
        'product_id': product_id,
        'user_id': user_id
    })

# Endpoint to add API usage
@app.route('/api/usage/<user_id>/<api_id>', methods=['POST'])
def add_api_usage(user_id, api_id):
    # Increment usage counter in Redis for the specific user and API
    redis_client.incr(f'usage:{user_id}:{api_id}')
    product_id = redis_client.smembers(f'subscriptions:{user_id}')
    if product_id:
        product_id = product_id.pop()
        product_id = product_id and product_id.decode('utf-8')
    else:
        product_id = None
    api_details = product_id and redis_client.hget(product_id, api_id)
    api_details = api_details and api_details.decode('utf-8')
    product_name = product_id and redis_client.hget('products', product_id)
    product_name = product_name and product_name.decode('utf-8')
    if product_id is None:
        return jsonify({'message': 'User member is not subscribed'}), 403
    elif product_name is None:
        return jsonify({'message': 'API product is not added'}), 403
    elif api_details is None:
        return jsonify({'message': 'API is not subscribed to Product'}), 403
    else:
        return jsonify({
            'message': 'API usage increased successfully for the User and API',
            # 'user_id': user_id,
            # 'api_id': api_id,
            # 'product_id': product_id,
            # 'api_details': api_details,
            # 'product_name': product_name
        }), 200

# Endpoint to check usage quota and enforce rate limiting
@app.route('/api/usage/<user_id>/<api_id>', methods=['GET'])
def check_usage_quota(user_id, api_id):
    # Get current usage count from Redis
    product_id = redis_client.smembers(f'subscriptions:{user_id}')
    if product_id:
        product_id = product_id.pop()
        product_id = product_id and product_id.decode('utf-8')
    else:
        product_id = None
    api_details = product_id and redis_client.hget(product_id, api_id)
    api_details = api_details and api_details.decode('utf-8')
    product_name = product_id and redis_client.hget('products', product_id)
    product_name = product_name and product_name.decode('utf-8')
    usage_count = int(redis_client.get(f'usage:{user_id}:{api_id}') or 0)
    # Get usage quota from Redis
    quota = int(redis_client.get(f'quota:{api_id}') or 1000)
    if product_id is None:
        return jsonify({'message': 'User member is not subscribed'}), 403
    elif product_name is None:
        return jsonify({'message': 'Product is not added'}), 403
    elif api_details is None:
        return jsonify({'message': 'API is not subscribed to Product'}), 403
    elif usage_count >= quota:
        return jsonify({'message': 'Usage quota exceeded'}), 403
    else:
        return jsonify({
            'message': 'API access allowed',
            'quota': quota,
            'usage_count': usage_count,
            'user_id': user_id,
            'api_id': api_id,
            'product_id': product_id,
            'api_details': api_details,
            'product_name': product_name
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
