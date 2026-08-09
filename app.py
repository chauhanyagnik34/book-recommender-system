from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np

popular_df        = pickle.load(open('popular.pkl',          'rb'))
pt                = pickle.load(open('pt.pkl',               'rb'))
books             = pickle.load(open('books.pkl',            'rb'))
similarity_scores = pickle.load(open('similarity_score.pkl', 'rb'))   # note: no 's'

app = Flask(__name__)

# ── Home ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author    = list(popular_df['Book-Author'].values),
                           image     = list(popular_df['Image-URL-M'].values),
                           votes     = list(popular_df['num_ratings'].values),
                           rating    = list(popular_df['avg_rating'].values))

# ── Recommend page (GET) ──────────────────────────────────────────
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

# ── All Books page ────────────────────────────────────────────────
@app.route('/all_books')
def all_books():
    """Show every book that exists in the recommender pivot table."""
    all_titles = pt.index.tolist()
    deduped    = books.drop_duplicates('Book-Title')
    deduped    = deduped[deduped['Book-Title'].isin(all_titles)]

    return render_template('all_books.html',
                           book_name = list(deduped['Book-Title'].values),
                           author    = list(deduped['Book-Author'].values),
                           image     = list(deduped['Image-URL-M'].values),
                           total     = len(deduped))

# ── Autocomplete endpoint ─────────────────────────────────────────
@app.route('/search_books')
def search_books():
    """Return up to 10 book titles that contain the query string."""
    query = request.args.get('q', '').strip().lower()
    if not query or len(query) < 2:
        return jsonify([])
    results = [t for t in pt.index.tolist() if query in t.lower()][:10]
    return jsonify(results)

# ── Recommend books (POST) ────────────────────────────────────────
@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input', '').strip()

    if not user_input:
        return render_template('recommend.html',
                               data=None,
                               searched_title='',
                               error='Please enter a book title.')

    # Case-insensitive match
    matches = np.where(pt.index.str.lower() == user_input.lower())[0]

    if len(matches) == 0:
        return render_template('recommend.html',
                               data=None,
                               searched_title=user_input,
                               error=f'"{user_input}" was not found. '
                                     'Please select a title from the suggestions.')

    index        = matches[0]
    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]   # top 5 recommendations

    data = []
    for i in similar_items:
        item    = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        deduped = temp_df.drop_duplicates('Book-Title')
        item.extend(list(deduped['Book-Title'].values))
        item.extend(list(deduped['Book-Author'].values))
        item.extend(list(deduped['Image-URL-M'].values))
        data.append(item)

    return render_template('recommend.html', data=data, searched_title=pt.index[index])


if __name__ == '__main__':
    app.run(debug=True)
