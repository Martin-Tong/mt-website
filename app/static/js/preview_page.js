window.addEventListener('DOMContentLoaded', ()=>{
  let qrcode = new QRCode({
    content: location.href,
    container: "svg-viewbox", //Responsive use
    join: true //Crisp rendering and 4-5x reduced file size
  });
  let svg = qrcode.svg();
  document.getElementById("qrcode_container").innerHTML = svg;
  let _root = document.querySelector('#comment')
  let _target = document.querySelector('#post-control')
  let _observer = new IntersectionObserver((entries)=>{
    if (entries[0].intersectionRatio >0) {
      _target.classList.remove('position-sticky')
    } else {
      _target.classList.add('position-sticky')
    }
  })
  _observer.observe(_root)
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