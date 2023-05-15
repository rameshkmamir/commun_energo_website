function updateConversationUser() {
    const selectElement = document.getElementById('names');
    const csrfToken = getCookie('csrftoken');
    const conversationId = selectElement.getAttribute('data-conversation-id');
    const selectedUser = selectElement.value;
    
    const request = new XMLHttpRequest();
    request.open('POST', '/messages/conversations/' + conversationId + '/update-conversation-user/');
    request.setRequestHeader('X-CSRFToken', csrfToken);
    request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    request.onload = function() {
      if (request.status === 200) {
      } else {
      }
    };
    const data = {
      user_id: selectedUser,
      conversation_id: conversationId
    };
    request.send(JSON.stringify(data));
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  