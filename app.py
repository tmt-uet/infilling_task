from flask import Flask, json, Response, request, render_template, send_file
from flask_cors import CORS
from infill import INFILL
from sentence_transformers import SentenceTransformer, util
import os


app = Flask(__name__)


def init_app():
    os.environ["CUDA_VISIBLE_DEVICES"]="1"
    CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config['infill'] = INFILL()
    app.config['SentenceTransformer'] = SentenceTransformer('roberta-large-nli-stsb-mean-tokens')

    print('init app done')


init_app()
def success_handle(code, error_message,  status, mimetype='application/json'):
    return Response(json.dumps({"code": code, "message": error_message, "status": status}), mimetype=mimetype)


def error_handle(code, error_message,  status, mimetype='application/json'):
    return Response(json.dumps({"code": code, "message": error_message, "status": status}),  mimetype=mimetype)
def get_score_sentence_highest_roberta(original_desc, candidate_sentences):
    # print('original_desc', original_desc)
    # print('type', type(candidate_sentences))
    # candidate_sentences = []
    # for i in range(10):
    #     # augmented_text = model_aug.augment(original_desc)
    #     print('aug', app.config['naw.SynonymAug.ppdb'].augment(original_desc))
    #     candidate_sentences.append(
    #         app.config['naw.SynonymAug.ppdb'].augment(original_desc))
    # print('candidate_sentences', candidate_sentences)
    candidate_embeddings = app.config['SentenceTransformer'].encode(
        candidate_sentences)
    embeddings2 = app.config['SentenceTransformer'].encode(original_desc)
    # print('candidate_embeddings', candidate_embeddings)
    # Compute cosine similarity between all pairs
    cos_sim = util.pytorch_cos_sim(embeddings2, candidate_embeddings)
    # print(cos_sim)
    # Add all pairs to a list with their cosine similarity score
    all_sentence_combinations = []
    # print('len', len(candidate_sentences))
    for i in range(len(candidate_sentences)):
        # print('i', i)
        # print(cos_sim[0][i])
        all_sentence_combinations.append([cos_sim[0][i], i])
    # Sort list by the highest cosine similarity score
    all_sentence_combinations = sorted(
        all_sentence_combinations, key=lambda x: x[0], reverse=True)
    result_after_embedding = []
    for each_sent in all_sentence_combinations:
        score,i = each_sent
        result_after_embedding.append(candidate_sentences[i])
        print(score, candidate_sentences[i])
    # print('result_after_embedding', result_after_embedding)
    return result_after_embedding
    # score, i = all_sentence_combinations[0]
    # print('candidate_sentences[i]', candidate_sentences[i])
    # return candidate_sentences[i]

@app.route('/api', methods=['GET'])
def homepage():
    return success_handle(1, "OK", "OK")

@app.route('/api/infilling_word', methods=['POST'])
def infilling_word():
    sentence = request.form['input']
    order = request.form['order']
    mask = request.form['mask']
    mask = mask.split(',')
    source = request.form['source']
    for each_mask in mask:
        if each_mask != 'word' and each_mask !='sent':
            return error_handle(2, "LỖI, KHÔNG ĐÚNG ĐỊNH DẠNG MASK", "ERROR_MASK")

    if order.isdigit() == False:
        return error_handle(2, "ORDER PHẢI LÀ CHỮ SỐ", "ERROR_SERVER")
    order = int(order)
    if order > 30:
        return error_handle(2, "CHỈ ĐƯỢC TRUYỀN ORDER NHỎ HƠN 30", "ERROR_SERVER")
    # try:
    results = app.config['infill'].infilling_word(sentence, order, mask)
    # print(results)

    results_roberta = get_score_sentence_highest_roberta(source, results)

    return_output = json.dumps({
    "code": 0,
    "data": results_roberta
    })

    return Response(return_output, status=200, mimetype='application/json')
    # except Exception as e:
    #     print(e)
    #     return error_handle(2, "LỖI, KHÔNG ĐÚNG ĐỊNH DẠNG", "ERROR_SERVER")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
