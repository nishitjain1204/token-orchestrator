from flask import Flask, jsonify , make_response
import uuid,datetime,random,time

app = Flask(__name__)

# Data structure to store keys and their status
keys = {}  
key_ids = set()
blocked_ids = set()

maxint = 2**63 - 1

def delete_expired_keys():
    while True:
        current_time = datetime.datetime.now()
        keys_to_delete = set()
        for key_id in keys:
            if (current_time - keys[key_id]['created_at']).seconds >= 60:
                if keys[key_id]['blocked']:
                    blocked_ids.remove(key_id)
                else:
                    key_ids.remove(key_id)
                
                keys_to_delete.add(key_id)
        
        for key_id in keys_to_delete:
            del keys[key_id]
            print("{} key deleted".format(key_id))
        
        time.sleep(15)

def unblock_keys():
    while True:
        current_time = datetime.datetime.now()
        keys_to_unblock = set()
        
        for key_id in blocked_ids:
            if (current_time - keys[key_id]['blocked_at']).seconds >= 20:
                keys_to_unblock.add(key_id)
        
        for key_id in keys_to_unblock:       
            key_ids.add(key_id)
            blocked_ids.remove(key_id)
            keys[key_id]['blocked'] = False
            keys[key_id]['blocked_at'] = None
            print("{} key unblocked".format(key_id))
        
        time.sleep(15) 
            


def initialize_key_body():
    
    while (key_id := random.randint(0,maxint)) in key_ids:
        continue
    
    key_ids.add(key_id)
    key_code = str(uuid.uuid4())
    
    key_body = {
        "id" : key_id,
        "code" : key_code,
        "created_at" : datetime.datetime.now(),
        "blocked" : False,
        "blocked_at" : None,
    }
    keys[key_id] = key_body
    
    return key_body

def create_response(key_id):
    obj = keys[key_id]
    return jsonify(obj)

# Endpoint to create a new key
@app.route('/create_key', methods=['POST'])
def create_key():
    return jsonify(initialize_key_body())

# Endpoint to retrieve an available key
@app.route('/get_key', methods=['GET'])
def get_key():
    
    if len(key_ids)>0:
        available_key_id = next(iter(key_ids))
    else:
        return make_response(
            jsonify({
            "error": "No available keys."}
        ),404)
    
    selected_key = keys[available_key_id]
    selected_key["blocked"] = True
    selected_key["blocked_at"] = datetime.datetime.now()
    key_ids.remove(available_key_id)
    blocked_ids.add(available_key_id)
    
    return jsonify(
        {
            "key_id" : keys[available_key_id]
        }
    )

@app.route('/get_key/<int:key_id>', methods=['GET'])
def get_key_details(key_id):
    
    if keys.get(key_id):
        if keys[key_id].get("deleted") is None:
            return create_response(key_id)
    else:
        return make_response(
            jsonify({
            "error": "Key not found."}
        ),404)

@app.route('/delete_key/<int:key_id>', methods=['DELETE'])
def delete_key_details(key_id):
    
    key_found= False
    
    if key_id in blocked_ids:
        blocked_ids.remove(key_id)
        key_found = True
    
    elif key_id in keys:
        key_ids.remove(key_id)
        key_found = True
    
    if key_found:
        del keys[key_id]
        return make_response(
            jsonify({
            "message": "Key deleted successfully."}
        ),200)
        
    else:
        return make_response(
            jsonify({
            "error": "Key not found."}
        ),404)

@app.route('/update/<int:key_id>', methods=['PUT'])
def update_key_status(key_id):
    
    if key_id in blocked_ids:
        blocked_ids.remove(key_id)
        key_ids.add(key_id)
        keys[key_id]['blocked'] = False
        keys[key_id]['blocked_at'] = None
        return create_response(key_id= key_id)
            
    else:
        return make_response(
            jsonify({
            "error": "Key not found."}
        ),404)

@app.route('/keepalive/<int:key_id>', methods=['PUT'])
def keep_alive(key_id):
    
    if keys.get(key_id):
        
        keys[key_id]["created_at"] = datetime.datetime.now()
        return jsonify(
            {
                "message" : "Key updated successfully."
            }
        )
            
    else:
        return make_response(
            jsonify({
            "error": "Key not found."}
        ),404)

    
    

if __name__ == '__main__':
    
    import threading
    
    background_thread_delete_expired = threading.Thread(target=delete_expired_keys)
    background_thread_delete_expired.daemon = True
    
    background_thread_unblock = threading.Thread(target=unblock_keys)
    background_thread_unblock.daemon = True
    
    background_thread_unblock.start()
    background_thread_delete_expired.start()
    
    # Run the Flask app
    app.run(debug=False)
