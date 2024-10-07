<script>
  import { httpRequest, httpUploadFile } from './HttpRequest.svelte';

  let datasets = [];
  let selectedDataset = '';
  let dataList = [];
  let currentPage = 1;
  const filesPerPage = 10;
  let totalCount = 0;
  let fileToUpload = null;

  async function fetchDatasets() {
    try {
      const ret = await httpRequest('/dataset/get', 'POST');
      if (ret.code === 0) {
        datasets = ret.data.dataset_list;
      }
    } catch (error) {
      console.error('获取文件集合失败:', error);
    }
  }

  async function fetchFiles() {
    try {
      const ret = await httpRequest('/data/get', 'POST', { dataset_id: selectedDataset, page_index: currentPage, page_size: filesPerPage });
      if (ret.code === 0) {
        dataList = ret.data.data_list;
        totalCount = ret.data.total_count;
      }
    } catch (error) {
      console.error('获取文件列表失败:', error);
    }
  }

  function handleFileUpload(event) {
    fileToUpload = event.target.files[0];
  }

  async function uploadFile() {
    if (!fileToUpload) {
      alert('请先选择文件');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileToUpload);
    formData.append('dataset_id', selectedDataset);

    try {
      const ret = await httpUploadFile('/data/add_file', formData);
      if (ret.code === 0) {
        alert('文件上传成功');
        fetchFiles();
      }
    } catch (error) {
      console.error('文件上传失败:', error);
    }
  }

  async function deleteData(dataId) {
    if (confirm('确认要删除该文件吗？')) {
      try {
        const ret = await httpRequest('/data/delete', 'POST', { id: dataId });
        if (ret.code === 0) {
          alert('文件删除成功');
          fetchFiles(); // 重新加载文件列表
        }
      } catch (error) {
        console.error('文件删除失败:', error);
      }
    }
  }

  function changePage(page) {
    currentPage = page;
    fetchFiles();
  }

  function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString(); // 可以根据需要自定义格式
  }

  $: if (selectedDataset) {
    fetchFiles();
  }

  fetchDatasets();
</script>

<style>
  /* 使用Skeleton的基础样式 */
  .table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eaeaea;
  }
  th {
    background-color: #f0f0f0; /* 灰色背景 */
    color: black; /* 黑色文字 */
  }
  th:hover {
    background-color: #d9d9d9; /* 悬停时稍微变暗 */
  }
  tr:hover {
    background-color: #f0f0f0;
  }
  .button {
    margin-top: 10px;
  }
</style>

<h1 class="text-xl font-bold mb-4">文件管理</h1>
<p class="mb-6">这里将实现文件管理的功能。</p>

<div class="mb-6">
  <label for="dataset-select" class="block mb-2">选择文件集合:</label>
  <select id="dataset-select" bind:value={selectedDataset} class="border p-2 rounded w-full">
    <option value="" disabled>请选择文件集合</option>
    {#each datasets as dataset}
      <option value={dataset.id}>{dataset.name}</option>
    {/each}
  </select>
</div>

<h2 class="text-lg font-semibold mb-2">文件列表</h2>
<table class="table">
  <thead>
    <tr>
      <th>文件名</th>
      <th>上传时间</th>
      <th>操作</th>
    </tr>
  </thead>
  <tbody>
    {#if dataList.length > 0}
      {#each dataList as file}
        <tr>
          <td>{file.name}</td>
          <td>{formatTimestamp(file.add_timestamp)}</td>
          <td>
            <button class="button bg-red-500 text-white rounded px-3 py-1" on:click={() => deleteData(file.id)}>删除</button>
          </td>
        </tr>
      {/each}
    {:else}
      <tr>
        <td colspan="3" class="text-center">当前没有文件</td>
      </tr>
    {/if}
  </tbody>
</table>

{#if totalCount > filesPerPage}
  <div class="mt-4">
    <button class="button bg-gray-300 rounded px-3 py-1" on:click={() => changePage(currentPage - 1)} disabled={currentPage === 1}>上一页</button>
    <span class="mx-2">第 {currentPage} 页</span>
    <button class="button bg-gray-300 rounded px-3 py-1" on:click={() => changePage(currentPage + 1)} disabled={currentPage * filesPerPage >= totalCount}>下一页</button>
  </div>
{/if}

<h2 class="text-lg font-semibold mt-6 mb-2">上传文件</h2>
<input type="file" on:change={handleFileUpload} class="border p-2 rounded mb-4" />
<button class="button bg-blue-500 text-white rounded px-3 py-1" on:click={uploadFile}>上传</button>


<!--文件列表头部的颜色，蓝底太扎眼了。改成会底黑字。-->
<!--<script>-->
<!--  import { httpRequest, httpUploadFile } from './HttpRequest.svelte';-->

<!--  let datasets = [];-->
<!--  let selectedDataset = '';-->
<!--  let dataList = [];-->
<!--  let currentPage = 1;-->
<!--  const filesPerPage = 10;-->
<!--  let totalCount = 0;-->
<!--  let fileToUpload = null;-->

<!--  async function fetchDatasets() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/dataset/get', 'POST');-->
<!--      if (ret.code === 0) {-->
<!--        datasets = ret.data.dataset_list;-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取文件集合失败:', error);-->
<!--    }-->
<!--  }-->

<!--  async function fetchFiles() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/data/get', 'POST', { dataset_id: selectedDataset, page_index: currentPage, page_size: filesPerPage });-->
<!--      if (ret.code === 0) {-->
<!--        dataList = ret.data.data_list;-->
<!--        totalCount = ret.data.total_count;-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取文件列表失败:', error);-->
<!--    }-->
<!--  }-->

<!--  function handleFileUpload(event) {-->
<!--    fileToUpload = event.target.files[0];-->
<!--  }-->

<!--  async function uploadFile() {-->
<!--    if (!fileToUpload) {-->
<!--      alert('请先选择文件');-->
<!--      return;-->
<!--    }-->

<!--    const formData = new FormData();-->
<!--    formData.append('file', fileToUpload);-->
<!--    formData.append('dataset_id', selectedDataset);-->

<!--    try {-->
<!--      const ret = await httpUploadFile('/data/add_file', formData);-->
<!--      if (ret.code === 0) {-->
<!--        alert('文件上传成功');-->
<!--        fetchFiles();-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('文件上传失败:', error);-->
<!--    }-->
<!--  }-->

<!--  async function deleteData(dataId) {-->
<!--    if (confirm('确认要删除该文件吗？')) {-->
<!--      try {-->
<!--        const ret = await httpRequest('/data/delete', 'POST', { id: dataId });-->
<!--        if (ret.code === 0) {-->
<!--          alert('文件删除成功');-->
<!--          fetchFiles(); // 重新加载文件列表-->
<!--        }-->
<!--      } catch (error) {-->
<!--        console.error('文件删除失败:', error);-->
<!--      }-->
<!--    }-->
<!--  }-->

<!--  function changePage(page) {-->
<!--    currentPage = page;-->
<!--    fetchFiles();-->
<!--  }-->

<!--  function formatTimestamp(timestamp) {-->
<!--    const date = new Date(timestamp);-->
<!--    return date.toLocaleString(); // 可以根据需要自定义格式-->
<!--  }-->

<!--  $: if (selectedDataset) {-->
<!--    fetchFiles();-->
<!--  }-->

<!--  fetchDatasets();-->
<!--</script>-->

<!--<style>-->
<!--  /* 使用Skeleton的基础样式 */-->
<!--  .table {-->
<!--    width: 100%;-->
<!--    border-collapse: collapse;-->
<!--  }-->
<!--  th, td {-->
<!--    padding: 12px;-->
<!--    text-align: left;-->
<!--    border-bottom: 1px solid #eaeaea;-->
<!--  }-->
<!--  th {-->
<!--    background-color: #007bff; /* 深色背景 */-->
<!--    color: white; /* 白色文字 */-->
<!--  }-->
<!--  th:hover {-->
<!--    background-color: #0056b3; /* 悬停时的深色背景 */-->
<!--  }-->
<!--  tr:hover {-->
<!--    background-color: #f0f0f0;-->
<!--  }-->
<!--  .button {-->
<!--    margin-top: 10px;-->
<!--  }-->
<!--</style>-->

<!--<h1 class="text-xl font-bold mb-4">文件管理</h1>-->
<!--<p class="mb-6">这里将实现文件管理的功能。</p>-->

<!--<div class="mb-6">-->
<!--  <label for="dataset-select" class="block mb-2">选择文件集合:</label>-->
<!--  <select id="dataset-select" bind:value={selectedDataset} class="border p-2 rounded w-full">-->
<!--    <option value="" disabled>请选择文件集合</option>-->
<!--    {#each datasets as dataset}-->
<!--      <option value={dataset.id}>{dataset.name}</option>-->
<!--    {/each}-->
<!--  </select>-->
<!--</div>-->

<!--<h2 class="text-lg font-semibold mb-2">文件列表</h2>-->
<!--<table class="table">-->
<!--  <thead>-->
<!--    <tr>-->
<!--      <th>文件名</th>-->
<!--      <th>上传时间</th>-->
<!--      <th>操作</th>-->
<!--    </tr>-->
<!--  </thead>-->
<!--  <tbody>-->
<!--    {#if dataList.length > 0}-->
<!--      {#each dataList as file}-->
<!--        <tr>-->
<!--          <td>{file.name}</td>-->
<!--          <td>{formatTimestamp(file.add_timestamp)}</td>-->
<!--          <td>-->
<!--            <button class="button bg-red-500 text-white rounded px-3 py-1" on:click={() => deleteData(file.id)}>删除</button>-->
<!--          </td>-->
<!--        </tr>-->
<!--      {/each}-->
<!--    {:else}-->
<!--      <tr>-->
<!--        <td colspan="3" class="text-center">当前没有文件</td>-->
<!--      </tr>-->
<!--    {/if}-->
<!--  </tbody>-->
<!--</table>-->

<!--{#if totalCount > filesPerPage}-->
<!--  <div class="mt-4">-->
<!--    <button class="button bg-gray-300 rounded px-3 py-1" on:click={() => changePage(currentPage - 1)} disabled={currentPage === 1}>上一页</button>-->
<!--    <span class="mx-2">第 {currentPage} 页</span>-->
<!--    <button class="button bg-gray-300 rounded px-3 py-1" on:click={() => changePage(currentPage + 1)} disabled={currentPage * filesPerPage >= totalCount}>下一页</button>-->
<!--  </div>-->
<!--{/if}-->

<!--<h2 class="text-lg font-semibold mt-6 mb-2">上传文件</h2>-->
<!--<input type="file" on:change={handleFileUpload} class="border p-2 rounded mb-4" />-->
<!--<button class="button bg-blue-500 text-white rounded px-3 py-1" on:click={uploadFile}>上传</button>-->


<!--文件列表的头部：文件名、上传时间和操作。文字和底色都太浅了，要鼠标悬浮在上边，才看得清。优化下。-->

<!--<script>-->
<!--  import { httpRequest, httpUploadFile } from './HttpRequest.svelte';-->

<!--  let datasets = [];-->
<!--  let selectedDataset = '';-->
<!--  let dataList = [];-->
<!--  let currentPage = 1;-->
<!--  const filesPerPage = 10;-->
<!--  let totalCount = 0;-->
<!--  let fileToUpload = null;-->

<!--  async function fetchDatasets() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/dataset/get', 'POST');-->
<!--      if (ret.code === 0) {-->
<!--        datasets = ret.data.dataset_list;-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取文件集合失败:', error);-->
<!--    }-->
<!--  }-->

<!--  async function fetchFiles() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/data/get', 'POST', { dataset_id: selectedDataset, page_index: currentPage, page_size: filesPerPage });-->
<!--      if (ret.code === 0) {-->
<!--        dataList = ret.data.data_list;-->
<!--        totalCount = ret.data.total_count;-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取文件列表失败:', error);-->
<!--    }-->
<!--  }-->

<!--  function handleFileUpload(event) {-->
<!--    fileToUpload = event.target.files[0];-->
<!--  }-->

<!--  async function uploadFile() {-->
<!--    if (!fileToUpload) {-->
<!--      alert('请先选择文件');-->
<!--      return;-->
<!--    }-->

<!--    const formData = new FormData();-->
<!--    formData.append('file', fileToUpload);-->
<!--    formData.append('dataset_id', selectedDataset);-->

<!--    try {-->
<!--      const ret = await httpUploadFile('/data/add_file', formData);-->
<!--      if (ret.code === 0) {-->
<!--        alert('文件上传成功');-->
<!--        fetchFiles();-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('文件上传失败:', error);-->
<!--    }-->
<!--  }-->

<!--  async function deleteData(dataId) {-->
<!--    if (confirm('确认要删除该文件吗？')) {-->
<!--      try {-->
<!--        const ret = await httpRequest('/data/delete', 'POST', { id: dataId });-->
<!--        if (ret.code === 0) {-->
<!--          alert('文件删除成功');-->
<!--          fetchFiles(); // 重新加载文件列表-->
<!--        }-->
<!--      } catch (error) {-->
<!--        console.error('文件删除失败:', error);-->
<!--      }-->
<!--    }-->
<!--  }-->

<!--  function changePage(page) {-->
<!--    currentPage = page;-->
<!--    fetchFiles();-->
<!--  }-->

<!--  function formatTimestamp(timestamp) {-->
<!--    const date = new Date(timestamp);-->
<!--    return date.toLocaleString(); // 可以根据需要自定义格式-->
<!--  }-->

<!--  $: if (selectedDataset) {-->
<!--    fetchFiles();-->
<!--  }-->

<!--  fetchDatasets();-->
<!--</script>-->

<!--<style>-->
<!--  /* 使用Skeleton的基础样式 */-->
<!--  .table {-->
<!--    width: 100%;-->
<!--    border-collapse: collapse;-->
<!--  }-->
<!--  th, td {-->
<!--    padding: 12px;-->
<!--    text-align: left;-->
<!--    border-bottom: 1px solid #eaeaea;-->
<!--  }-->
<!--  th {-->
<!--    background-color: var(&#45;&#45;skeleton-color);-->
<!--    color: white;-->
<!--  }-->
<!--  tr:hover {-->
<!--    background-color: #f0f0f0;-->
<!--  }-->
<!--  .button {-->
<!--    margin-top: 10px;-->
<!--  }-->
<!--</style>-->

<!--<h1 class="text-xl font-bold mb-4">文件管理</h1>-->
<!--<p class="mb-6">这里将实现文件管理的功能。</p>-->

<!--<div class="mb-6">-->
<!--  <label for="dataset-select" class="block mb-2">选择文件集合:</label>-->
<!--  <select id="dataset-select" bind:value={selectedDataset} class="border p-2 rounded w-full">-->
<!--    <option value="" disabled>请选择文件集合</option>-->
<!--    {#each datasets as dataset}-->
<!--      <option value={dataset.id}>{dataset.name}</option>-->
<!--    {/each}-->
<!--  </select>-->
<!--</div>-->

<!--<h2 class="text-lg font-semibold mb-2">文件列表</h2>-->
<!--<table class="table">-->
<!--  <thead>-->
<!--    <tr>-->
<!--      <th>文件名</th>-->
<!--      <th>上传时间</th>-->
<!--      <th>操作</th>-->
<!--    </tr>-->
<!--  </thead>-->
<!--  <tbody>-->
<!--    {#if dataList.length > 0}-->
<!--      {#each dataList as file}-->
<!--        <tr>-->
<!--          <td>{file.name}</td>-->
<!--          <td>{formatTimestamp(file.add_timestamp)}</td>-->
<!--          <td>-->
<!--            <button class="button bg-red-500 text-white rounded px-3 py-1" on:click={() => deleteData(file.id)}>删除</button>-->
<!--          </td>-->
<!--        </tr>-->
<!--      {/each}-->
<!--    {:else}-->
<!--      <tr>-->
<!--        <td colspan="3" class="text-center">当前没有文件</td>-->
<!--      </tr>-->
<!--    {/if}-->
<!--  </tbody>-->
<!--</table>-->

<!--{#if totalCount > filesPerPage}-->
<!--  <div class="mt-4">-->
<!--    <button class="button bg-gray-300 rounded px-3 py-1" on:click={() => changePage(currentPage - 1)} disabled={currentPage === 1}>上一页</button>-->
<!--    <span class="mx-2">第 {currentPage} 页</span>-->
<!--    <button class="button bg-gray-300 rounded px-3 py-1" on:click={() => changePage(currentPage + 1)} disabled={currentPage * filesPerPage >= totalCount}>下一页</button>-->
<!--  </div>-->
<!--{/if}-->

<!--<h2 class="text-lg font-semibold mt-6 mb-2">上传文件</h2>-->
<!--<input type="file" on:change={handleFileUpload} class="border p-2 rounded mb-4" />-->
<!--<button class="button bg-blue-500 text-white rounded px-3 py-1" on:click={uploadFile}>上传</button>-->



<!--<script>-->
<!--  import { httpRequest, httpUploadFile } from './HttpRequest.svelte';-->

<!--  let datasets = [];-->
<!--  let selectedDataset = '';-->
<!--  let dataList = [];-->
<!--  let currentPage = 1;-->
<!--  const filesPerPage = 10;-->
<!--  let totalCount = 0;-->
<!--  let fileToUpload = null;-->

<!--  async function fetchDatasets() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/dataset/get', 'POST');-->
<!--      if (ret.code === 0) {-->
<!--        datasets = ret.data.dataset_list;-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取文件集合失败:', error);-->
<!--    }-->
<!--  }-->

<!--  async function fetchFiles() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/data/get', 'POST', { dataset_id: selectedDataset, page_index: currentPage, page_size: filesPerPage });-->
<!--      if (ret.code === 0) {-->
<!--        dataList = ret.data.data_list;-->
<!--        totalCount = ret.data.total_count;-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取文件列表失败:', error);-->
<!--    }-->
<!--  }-->

<!--  function handleFileUpload(event) {-->
<!--    fileToUpload = event.target.files[0];-->
<!--  }-->

<!--  async function uploadFile() {-->
<!--    if (!fileToUpload) {-->
<!--      alert('请先选择文件');-->
<!--      return;-->
<!--    }-->

<!--    const formData = new FormData();-->
<!--    formData.append('file', fileToUpload);-->
<!--    formData.append('dataset_id', selectedDataset);-->

<!--    try {-->
<!--      const ret = await httpUploadFile('/data/add_file', formData);-->
<!--      if (ret.code === 0) {-->
<!--        alert('文件上传成功');-->
<!--        fetchFiles();-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('文件上传失败:', error);-->
<!--    }-->
<!--  }-->

<!--  async function deleteData(dataId) {-->
<!--    if (confirm('确认要删除该文件吗？')) {-->
<!--      try {-->
<!--        const ret = await httpRequest('/data/delete', 'POST', { id: dataId });-->
<!--        if (ret.code === 0) {-->
<!--          alert('文件删除成功');-->
<!--          fetchFiles(); // 重新加载文件列表-->
<!--        }-->
<!--      } catch (error) {-->
<!--        console.error('文件删除失败:', error);-->
<!--      }-->
<!--    }-->
<!--  }-->

<!--  function changePage(page) {-->
<!--    currentPage = page;-->
<!--    fetchFiles();-->
<!--  }-->

<!--  function formatTimestamp(timestamp) {-->
<!--    const date = new Date(timestamp);-->
<!--    return date.toLocaleString(); // 可以根据需要自定义格式-->
<!--  }-->

<!--  $: if (selectedDataset) {-->
<!--    fetchFiles();-->
<!--  }-->

<!--  fetchDatasets();-->
<!--</script>-->

<!--<style>-->
<!--  table {-->
<!--    width: 100%;-->
<!--    border-collapse: collapse;-->
<!--  }-->
<!--  th, td {-->
<!--    border: 1px solid #ddd;-->
<!--    padding: 8px;-->
<!--    text-align: left;-->
<!--  }-->
<!--  th {-->
<!--    background-color: #f2f2f2;-->
<!--  }-->
<!--  tr:hover {-->
<!--    background-color: #f5f5f5;-->
<!--  }-->
<!--</style>-->

<!--<h1>文件管理</h1>-->
<!--<p>这里将实现文件管理的功能。</p>-->

<!--<div>-->
<!--  <label for="dataset-select">选择文件集合:</label>-->
<!--  <select id="dataset-select" bind:value={selectedDataset}>-->
<!--    <option value="" disabled>请选择文件集合</option>-->
<!--    {#each datasets as dataset}-->
<!--      <option value={dataset.id}>{dataset.name}</option>-->
<!--    {/each}-->
<!--  </select>-->
<!--</div>-->

<!--<h2>文件列表</h2>-->
<!--<table>-->
<!--  <thead>-->
<!--    <tr>-->
<!--      <th>文件名</th>-->
<!--      <th>上传时间</th>-->
<!--      <th>操作</th>-->
<!--    </tr>-->
<!--  </thead>-->
<!--  <tbody>-->
<!--    {#if dataList.length > 0}-->
<!--      {#each dataList as file}-->
<!--        <tr>-->
<!--          <td>{file.name}</td>-->
<!--          <td>{formatTimestamp(file.add_timestamp)}</td>-->
<!--          <td>-->
<!--            <button on:click={() => deleteData(file.id)}>删除</button>-->
<!--          </td>-->
<!--        </tr>-->
<!--      {/each}-->
<!--    {:else}-->
<!--      <tr>-->
<!--        <td colspan="3">当前没有文件</td>-->
<!--      </tr>-->
<!--    {/if}-->
<!--  </tbody>-->
<!--</table>-->

<!--{#if totalCount > filesPerPage}-->
<!--  <div>-->
<!--    <button on:click={() => changePage(currentPage - 1)} disabled={currentPage === 1}>上一页</button>-->
<!--    <span>第 {currentPage} 页</span>-->
<!--    <button on:click={() => changePage(currentPage + 1)} disabled={currentPage * filesPerPage >= totalCount}>下一页</button>-->
<!--  </div>-->
<!--{/if}-->

<!--<h2>上传文件</h2>-->
<!--<input type="file" on:change={handleFileUpload} />-->
<!--<button on:click={uploadFile}>上传</button>-->
