window.addEventListener('DOMContentLoaded', ()=>{
  let qrcode = new QRCode({
    content: location.href,
    container: "svg-viewbox", //Responsive use
    join: true //Crisp rendering and 4-5x reduced file size
  });
  document.getElementById("qrcode_container").innerHTML = qrcode.svg();
  let _root = document.querySelector('#comment')
  let _target = document.querySelector('#post-control')
  let html_content = document.querySelectorAll('#post_content code')
  for (let i=0; i < html_content.length; i++) {
    html_content[i].innerText = html_content[i].innerText.replaceAll("&lt;", "<").replaceAll("&gt;", ">")
  }
  let _observer = new IntersectionObserver((entries)=>{
    if (entries[0].intersectionRatio >0) {
      _target.classList.remove('position-sticky')
    } else {
      _target.classList.add('position-sticky')
    }
  })
  _observer.observe(_root)
  load_comments()
})

const myModal = new bootstrap.Modal('#global-modal', {backdrop:'static',keyboard: false})
let _confirm = document.querySelector('#global-modal #confirm')
_confirm.addEventListener('click', (e)=>{
  if (sessionStorage.getItem(location.href)) {
    e.preventDefault()
    e.stopPropagation()
    _noc_utils.noc_alert('文章已删除', 'success',1)
  } else {
    fetch(`${location.href}/delete`, {credentials: 'same-origin',headers:{'N-From-Fetch':1}}).then((res)=>{
      return res.json()
    }).then((res)=>{
      switch (res.message) {
        case '文章删除成功':
          _noc_utils.noc_alert('删除成功，即将返回首页', 'success')
          sessionStorage.setItem(location.href, true)
          setTimeout(()=>{location.href = location.origin}, 1000)
          return
        case '删除失败，请检查参数后重试':
          _noc_utils.noc_alert('删除失败，请检查参数后重试', 'error')
          return
      }
    })
  }
  myModal.hide()
})

let _submit_comment = document.querySelector('#comment-input + button')
if (noc_user_status) {
  _submit_comment.addEventListener('click', (e)=>{
    post_comment()
  })
} else {
  _submit_comment.attributes.setNamedItem(document.createAttribute('disabled'))
}

function load_comments() {
  let id = location.href.split('/').pop()
  fetch(`${location.origin}/post/${id}/comments`, {
      withCredentials: 'same-origin',
      headers:{'N-From-Fetch':1
    }}).then((res)=>{
      return res.json()
  }).then((res)=>{
    let _comment = document.querySelector('#comment')
    if (res.comments.length === 0) {
      _comment.innerHTML = `<div class="text-center">暂无评论</div>`
    } else {
      _comment.innerHTML = ''
      for (let i = 0; i < res.comments.length; i++) {
        let _div = document.createElement('div')
        _div.className = 'card px-3 mb-3 border-0'
        _div.dataset.commentId = res.comments[i].id
        _div.innerHTML = `
          <div class="card-body p-0">
            <h5 class="card-title fs-6">@${res.comments[i].author}&nbsp;&nbsp;<span class="comment-time">${new Date(res.comments[i].time*1000).toLocaleString()}</h5>
            <p class="card-text">${res.comments[i].content}</p>
            <p class="divider w-90"></p>
          </div>`
        _comment.appendChild(_div)
      }
    }
  })
}
function post_comment() {
  let id = location.href.split('/').pop()
  let _comment = document.querySelector('#comment-input')
  let _content = _comment.value
  if (_content === '') {
    _noc_utils.noc_alert('评论内容不能为空', 'warning',  true)
    return
  }
  fetch(`${location.origin}/post/${id}/comments`, {
    method: 'POST',
    withCredentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'N-From-Fetch': 1
    },
    body: JSON.stringify({comments: _content})
  }).then((res)=>{
    return res.json()
  }).then((res)=>{
    if (res.message === '评论成功') {
      _noc_utils.noc_alert('评论成功', 'success',  true)
      load_comments()
      _comment.value = ''
    }
  })
}
let textarea = document.querySelector('#comment-input')
textarea.addEventListener('emojiSelected', (e)=>{
    textarea.value += e.detail.emoji
    textarea.focus()
})