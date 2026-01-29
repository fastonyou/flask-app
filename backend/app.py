@app.route('/status')
def status():
    return jsonify({
        'status': 'oneline',
        'version': '1.0.0',
        'uptime': 'healthy'
    })
