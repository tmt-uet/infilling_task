from flask import Flask, json, Response, request, render_template, send_file
from flask_cors import CORS
from infill import INFILL
app = Flask(__name__)


def init_app():
    CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config['infill'] = INFILL()
    print('init app done')


init_app()
def success_handle(code, error_message,  status, mimetype='application/json'):
    return Response(json.dumps({"code": code, "message": error_message, "status": status}), mimetype=mimetype)


def error_handle(code, error_message,  status, mimetype='application/json'):
    return Response(json.dumps({"code": code, "message": error_message, "status": status}),  mimetype=mimetype)

@app.route('/api', methods=['GET'])
def homepage():
    return success_handle(1, "OK", "OK")

@app.route('/api/infill_sentence', methods=['POST'])
def infill_sentence():
    sentence = request.form['input']
    order = request.form['order']

    if order.isdigit() == False:
        return error_handle(2, "ORDER PHẢI LÀ CHỮ SỐ", "ERROR_SERVER")
    order = int(order)
    if order > 15:
        return error_handle(2, "CHỈ ĐƯỢC TRUYỀN ORDER NHỎ HƠN 15", "ERROR_SERVER")
    try:
        results = str(app.config['infill'].infilling_sentence(sentence, order))
        print(results)

        return_output = json.dumps({
        "code": 0,
        "data": results
        })

        return Response(return_output, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return error_handle(2, "LỖI, KHÔNG ĐÚNG ĐỊNH DẠNG", "ERROR_SERVER")
@app.route('/api/infilling_word', methods=['POST'])
def infilling_word():
    sentence = request.form['input']
    order = request.form['order']
    mask = request.form['mask']
    mask = mask.split(',')
    for each_mask in mask:
        if each_mask != 'word' and each_mask !='sent':
            return error_handle(2, "LỖI, KHÔNG ĐÚNG ĐỊNH DẠNG MASK", "ERROR_MASK")

    if order.isdigit() == False:
        return error_handle(2, "ORDER PHẢI LÀ CHỮ SỐ", "ERROR_SERVER")
    order = int(order)
    if order > 30:
        return error_handle(2, "CHỈ ĐƯỢC TRUYỀN ORDER NHỎ HƠN 30", "ERROR_SERVER")
    # try:
    results = str(app.config['infill'].infilling_word(sentence, order, mask))
    print(results)

    return_output = json.dumps({
    "code": 0,
    "data": results
    })

    return Response(return_output, status=200, mimetype='application/json')
    # except Exception as e:
    #     print(e)
    #     return error_handle(2, "LỖI, KHÔNG ĐÚNG ĐỊNH DẠNG", "ERROR_SERVER")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
