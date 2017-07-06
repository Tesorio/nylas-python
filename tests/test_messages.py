import json
import six
import pytest
import responses


@responses.activate
@pytest.mark.usefixtures("mock_messages")
def test_messages(api_client):
    message = api_client.messages.first()
    assert len(message.labels) == 1
    assert message.labels[0].display_name == 'Inbox'
    assert message.folder is None
    assert message.unread
    assert not message.starred


@responses.activate
@pytest.mark.usefixtures("mock_account", "mock_messages", "mock_message")
def test_message_change(api_client):
    message = api_client.messages.first()
    message.star()
    assert message.starred is True
    message.unstar()
    assert message.starred is False
    message.mark_as_read()
    assert message

    message.add_label('fghj')
    msg_labels = [l.id for l in message.labels]
    assert 'abcd' in msg_labels
    assert 'fghj' in msg_labels
    message.remove_label('fghj')
    msg_labels = [l.id for l in message.labels]
    assert 'abcd' in msg_labels
    assert 'fghj' not in msg_labels

    # Test that folders don't do anything when labels are in effect
    message.update_folder('zxcv')
    assert message.folder is None


@responses.activate
@pytest.mark.usefixtures("mock_account", "mock_messages", "mock_message")
def test_message_raw(api_client, account_id):
    message = api_client.messages.first()
    assert isinstance(message.raw, six.binary_type)
    parsed = json.loads(message.raw)
    assert parsed == [{
        "object": "message",
        "account_id": account_id,
        "labels": [{
            "display_name": "Inbox",
            "name": "inbox",
            "id": "abcd",
        }],
        "starred": False,
        "unread": True,
        "id": "1234",
        "subject": "Test Message"
    }]
