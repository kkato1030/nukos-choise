import boto3
import json
import random
import urllib.request


with open('./config.json') as f:
    config = json.loads(f.read())

url = config['url']
members = config['members']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('OrderTable')


def main(event=None, context=None):
    member = get_member()
    if not len(member):
        save_order(members)
        member = get_member()

    delete_member(member)

    msg = f"今日のふぁしり <@{member['name']}>"
    post_slack(msg)


def save_order(members):
    random.shuffle(members)
    with table.batch_writer() as batch:
        for i in range(len(members)):
            batch.put_item(
                Item={
                    'order': i+1,
                    'name': members[i],
                }
            )


def get_member():
    res = table.scan()
    items = res['Items']
    if not len(items):
        return {}

    sorted_items = sorted(items, key=lambda i: i['order'])
    return sorted_items[0]


def delete_member(member):
    order = member['order']
    table.delete_item(
        Key={
            'order': order
        }
    )


def post_slack(msg):
    method = 'POST'
    request_headers = {'Content-Type': 'application/json; charset=utf-8'}
    body = json.dumps({'text': msg}).encode("utf-8")
    request = urllib.request.Request(
        url=url,
        data=body,
        method=method,
        headers=request_headers
    )
    urllib.request.urlopen(request)


if __name__ == '__main__':
    main()
