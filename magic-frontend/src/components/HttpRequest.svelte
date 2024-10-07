<!-- HttpRequest.svelte -->
<script context="module">
  export async function httpRequest(path, method, body = {}, headers = {}) {
    const response = await fetch(`${API_HOST}${path}`, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'user_id': USER_ID || '', // 添加 user_id 作为请求头
        ...headers,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`请求失败: ${response.statusText}`);
    }

    return response.json();
  }

  export async function httpUploadFile(path, formData, headers = {}) {
    const response = await fetch(`${API_HOST}${path}`, {
      method: 'POST',
      headers: {
        'user_id': USER_ID || '', // 添加 user_id 作为请求头
        ...headers,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`文件上传失败: ${response.statusText}`);
    }

    return response.json();
  }
</script>

<script>
  import { API_HOST, USER_ID } from '../js/config.js';
</script>

<!--添加一个httpUploadFile功能，采用form-data Content-Type来上传文件，header中要可以输入user_id，form-data还有另一参数dataset_id。-->
<!--&lt;!&ndash; HttpRequest.svelte &ndash;&gt;-->
<!--<script context="module">-->
<!--  export async function httpRequest(path, method, body = {}, headers = {}) {-->
<!--    const response = await fetch(`${API_HOST}${path}`, {-->
<!--      method: method,-->
<!--      headers: {-->
<!--        'Content-Type': 'application/json',-->
<!--        'user_id': USER_ID || '', // 添加 user_id 作为请求头-->
<!--        ...headers,-->
<!--      },-->
<!--      body: JSON.stringify(body),-->
<!--    });-->

<!--    if (!response.ok) {-->
<!--      throw new Error(`请求失败: ${response.statusText}`);-->
<!--    }-->

<!--    return response.json();-->
<!--  }-->
<!--</script>-->

<!--<script>-->
<!--  import { API_HOST, USER_ID } from '../js/js.js';-->
<!--</script>-->
