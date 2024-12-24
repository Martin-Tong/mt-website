function add_notices() {
    let button = document.querySelector('#get-notices')
    let _input = document.querySelector('#notices-input')
    button.addEventListener('click',(e)=>{
        e.preventDefault()
        if (!_input.value.trim()) {
            _input.classList.add('is-invalid')
            return
        }
        if (_input.classList.contains('is-invalid')) {
            _input.classList.remove('is-invalid')
        }
        let form =new FormData()
        form.append('data', _input.value.trim())
        fetch(location.origin+'/notices', {
            headers:{
                'N-From-Fetch':1
            },
            withCredentials: 'same-origin',
            method: 'post',
            body: form
        }).then(res=>{
            return res.json()
        }).then(res=>{
            if (res.status == 'success') {
                //_noc_utils.noc_alert('记录成功', 'success', 1)
                update_session_notices({'content':_input.value, 'time': new Date().toLocaleString()})
                render_notices(JSON.stringify([{'content':_input.value, 'time': new Date().toLocaleString()}]), true)
            } else {
                //_noc_utils.noc_alert('记录失败，请稍后或刷新页面后重试', 'error', 1)
                console.log('发布随记失败')
            }
        })
    })
}

async function get_notices() {
    if (sessionStorage.getItem('notices')) {return sessionStorage.getItem('notices')}
    let data = await fetch(location.origin+'/notices', {
        method: 'get'
    })
    let _data = await data.json()
    sessionStorage.setItem('notices', JSON.stringify(_data))
    return JSON.stringify(_data)
}

function render_notices(data, animation=false) {
    let container = document.querySelector('#notices-content')
    let contents = []
    data = JSON.parse(data)
    for (let i=0; i < data.length; i++) {
        let _html = `<div class="mb-2 ${animation?'animate__animated animate__bounceInUp': ''}">                    
                                <p class="shadow text-truncate notice-title" data-notice-date="${new Date(Number(data[i].time)*1000).toLocaleString()}">${data[i].content}</p>                
                            </div>`
        let _html_1 = document.createElement('div')
        _html_1.innerHTML = _html

        // let _list = _html_1.querySelector('p')
        // _list.style.backgroundColor = `rgb(${Math.floor(Math.random()*100)},${Math.floor(Math.random()*175)},${Math.floor(Math.random()*255)})`

        contents.push(_html_1)
    }
    if (animation) {
        update_notices_item(container, contents)
    } else {
        contents.map((i)=>{
            container.appendChild(i)
        })
    }
}

function update_notices_item(container, target) {
    let index = 0
    let length = target.length
    function render() {
        let _target = target[index]
        if (index < length) {
            container.appendChild(_target)
            _target.onanimationend = ()=>{
                index += 1
                render()
            }
        } else {
            return
        }
    }
    render()
}

function update_session_notices(data) {
    let _data = JSON.parse(sessionStorage.getItem('notices'))
    _data.unshift(data)
    sessionStorage.setItem('notices', JSON.stringify(_data))
}

function input_behavior(e) {
    let target = e.target
    if (target.value.trim()) {
        let _clear = document.querySelector('#notices-input-clear')
        _clear.classList.remove('invisible')
    }
}
function input_clear_behavior(e) {
    let _input = document.querySelector('#notices-input')
    _input.value = null
    e.target.classList.add('invisible')
}

document.addEventListener('DOMContentLoaded', async ()=>{
    let target = document.querySelector('#notices-content')
    let _input = document.querySelector('#notices-input')
    let _clear = document.querySelector('#notices-input-clear')
    let button = document.querySelector('#get-notices')
    let data = await get_notices()
    let _timeout = setTimeout(()=>{
        target.removeAttribute('name')
        clearTimeout(_timeout)
    }, 500)
    if (_input) {
        if (noc_user_status) {
            _input.removeAttribute('disabled')
            button.removeAttribute('disabled')
        }
        add_notices()
        _input.oninput = input_behavior
        _clear.onclick = input_clear_behavior
        render_notices(data)
    } else {
        render_notices(data, true)
    }
})

