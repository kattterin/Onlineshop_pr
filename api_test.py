from requests import get, post, delete

# print(get('http://localhost:8080/api/good').json())
# print(get('http://localhost:8080/api/good/1').json())
# print(get('http://localhost:8080/api/good/q').json())

# print(post('http://localhost:8080/api/good',
#            json={'title': 'новости',
#                  'user_id': 1,
#                  'price': 344,
#                  'content': 'Текст новости',
#                  'old_price': 1345,
#                  'in_stock': 222
#                  }).json())
# parser.add_argument('title', required=True)
# parser.add_argument('content', required=True)
# parser.add_argument('user_id', required=True, type=int)
# parser.add_argument('price', required=True, type=int)
# parser.add_argument('old_price', required=True, type=int)
# parser.add_argument('in_stock', required=True, type=int)
# print(delete('http://localhost:8080/api/good/999').json())
#
# print(delete('http://localhost:8080/api/good/4').json())