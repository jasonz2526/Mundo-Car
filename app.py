from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 


@app.route('/player-stats', methods=['GET'])
def get_player_stats():
    data = pd.read_csv('more_info.csv')

    data['Duration'] = data['Duration'].round()
    duration_win_data = data.groupby('Duration').agg(
        win_count=('Win', 'sum'),
        match_count=('Duration', 'size')
    ).reset_index()

    duration_win_data['win_rate'] = (duration_win_data['win_count'] / duration_win_data['match_count']) * 100
    duration_win_data['radius'] = (duration_win_data['match_count'] ** 0.5) * 2

    data = duration_win_data.to_dict(orient='records')
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)