<script>
  import { httpRequest } from './HttpRequest.svelte';

  let connectors = []; // 存储数据连接器列表
  let currentPage = 1; // 当前页码
  const connectorsPerPage = 10; // 每页显示连接器数量
  let totalCount = 0; // 总连接器数量
  let newConnector = { name: '', url: '', type: 'mysql' }; // 新连接器的参数

  // 获取数据连接器列表
  async function fetchConnectors() {
    try {
      const ret = await httpRequest('/data_connector/get', 'POST', { page_index: currentPage, page_size: connectorsPerPage });
      if (ret.code === 0) {
        connectors = ret.data.data_connector_list;
        totalCount = ret.data.total_count; // 总连接器数量
      }
    } catch (error) {
      console.error('获取连接器失败:', error);
    }
  }

  // 添加数据连接器
  async function addConnector() {
    if (!newConnector.name || !newConnector.url) {
      alert('请填写所有字段');
      return;
    }

    try {
      const ret = await httpRequest('/data_connector/add', 'POST', newConnector);
      if (ret.code === 0) {
        alert('连接器添加成功');
        newConnector = { name: '', url: '', type: 'mysql' }; // 重置新连接器
        fetchConnectors(); // 重新获取连接器列表
      }
    } catch (error) {
      console.error('添加连接器失败:', error);
    }
  }

  // 删除数据连接器
  async function deleteConnector(connectorId) {
    if (confirm('确认要删除该连接器吗？')) {
      try {
        const ret = await httpRequest('/data_connector/delete', 'POST', { id: connectorId });
        if (ret.code === 0) {
          alert('连接器删除成功');
          fetchConnectors(); // 重新获取连接器列表
        }
      } catch (error) {
        console.error('连接器删除失败:', error);
      }
    }
  }

  // 切换页码
  function changePage(page) {
    currentPage = page;
    fetchConnectors();
  }

  // 初始化时获取连接器列表
  fetchConnectors();
</script>

<style>
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }
  th {
    background-color: #f0f0f0; /* 灰色背景 */
    color: black; /* 黑色文字 */
  }
  tr:hover {
    background-color: #f5f5f5;
  }
  .button {
    margin-top: 10px;
  }
</style>

<h1>数据连接器管理</h1>

<h2>连接器列表</h2>
<table>
  <thead>
    <tr>
      <th>名称</th>
      <th>URL</th>
      <th>类型</th>
      <th>操作</th>
    </tr>
  </thead>
  <tbody>
    {#if connectors.length > 0}
      {#each connectors as connector}
        <tr>
          <td>{connector.name}</td>
          <td>{connector.url}</td>
          <td>{connector.type}</td>
          <td>
            <button on:click={() => deleteConnector(connector.id)}>删除</button>
          </td>
        </tr>
      {/each}
    {:else}
      <tr>
        <td colspan="4" class="text-center">当前没有连接器</td>
      </tr>
    {/if}
  </tbody>
</table>

{#if totalCount > connectorsPerPage}
  <div>
    <button on:click={() => changePage(currentPage - 1)} disabled={currentPage === 1}>上一页</button>
    <span>第 {currentPage} 页</span>
    <button on:click={() => changePage(currentPage + 1)} disabled={currentPage * connectorsPerPage >= totalCount}>下一页</button>
  </div>
{/if}

<h2>添加数据连接器</h2>
<div>
  <label for="connector-name">名称:</label>
  <input id="connector-name" type="text" bind:value={newConnector.name} />

  <label for="connector-url">URL:</label>
  <input id="connector-url" type="text" bind:value={newConnector.url} />

  <label for="connector-type">类型:</label>
  <select id="connector-type" bind:value={newConnector.type}>
    <option value="mysql">MySQL</option>
    <option value="postgresql">PostgreSQL</option>
    <option value="sqlite">SQLite</option>
  </select>

  <button class="button bg-blue-500 text-white rounded px-3 py-1" on:click={addConnector}>添加连接器</button>
</div>

<!--参照上边的处理办法，对这个组件也用skeleton进行显示效果优化。-->
<!--<script>-->
<!--  import { httpRequest } from './HttpRequest.svelte';-->

<!--  let connectors = []; // 存储数据连接器列表-->
<!--  let currentPage = 1; // 当前页码-->
<!--  const connectorsPerPage = 10; // 每页显示连接器数量-->
<!--  let totalCount = 0; // 总连接器数量-->
<!--  let newConnector = { name: '', url: '', type: 'mysql' }; // 新连接器的参数-->

<!--  // 获取数据连接器列表-->
<!--  async function fetchConnectors() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/data_connector/get', 'POST', { page_index: currentPage, page_size: connectorsPerPage });-->
<!--      if (ret.code === 0) {-->
<!--        connectors = ret.data.data_connector_list;-->
<!--        totalCount = ret.data.total_count; // 总连接器数量-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取连接器失败:', error);-->
<!--    }-->
<!--  }-->

<!--  // 添加数据连接器-->
<!--  async function addConnector() {-->
<!--    if (!newConnector.name || !newConnector.url) {-->
<!--      alert('请填写所有字段');-->
<!--      return;-->
<!--    }-->

<!--    try {-->
<!--      const ret = await httpRequest('/data_connector/add', 'POST', newConnector);-->
<!--      if (ret.code === 0) {-->
<!--        alert('连接器添加成功');-->
<!--        newConnector = { name: '', url: '', type: 'mysql' }; // 重置新连接器-->
<!--        fetchConnectors(); // 重新获取连接器列表-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('添加连接器失败:', error);-->
<!--    }-->
<!--  }-->

<!--  // 删除数据连接器-->
<!--  async function deleteConnector(connectorId) {-->
<!--    if (confirm('确认要删除该连接器吗？')) {-->
<!--      try {-->
<!--        const ret = await httpRequest('/data_connector/delete', 'POST', { id: connectorId });-->
<!--        if (ret.code === 0) {-->
<!--          alert('连接器删除成功');-->
<!--          fetchConnectors(); // 重新获取连接器列表-->
<!--        }-->
<!--      } catch (error) {-->
<!--        console.error('连接器删除失败:', error);-->
<!--      }-->
<!--    }-->
<!--  }-->

<!--  // 切换页码-->
<!--  function changePage(page) {-->
<!--    currentPage = page;-->
<!--    fetchConnectors();-->
<!--  }-->

<!--  // 初始化时获取连接器列表-->
<!--  fetchConnectors();-->
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

<!--<h1>数据连接器管理</h1>-->

<!--<h2>连接器列表</h2>-->
<!--<table>-->
<!--  <thead>-->
<!--    <tr>-->
<!--      <th>名称</th>-->
<!--      <th>URL</th>-->
<!--      <th>类型</th>-->
<!--      <th>操作</th>-->
<!--    </tr>-->
<!--  </thead>-->
<!--  <tbody>-->
<!--    {#if connectors.length > 0}-->
<!--      {#each connectors as connector}-->
<!--        <tr>-->
<!--          <td>{connector.name}</td>-->
<!--          <td>{connector.url}</td>-->
<!--          <td>{connector.type}</td>-->
<!--          <td>-->
<!--            <button on:click={() => deleteConnector(connector.id)}>删除</button>-->
<!--          </td>-->
<!--        </tr>-->
<!--      {/each}-->
<!--    {:else}-->
<!--      <tr>-->
<!--        <td colspan="4">当前没有连接器</td>-->
<!--      </tr>-->
<!--    {/if}-->
<!--  </tbody>-->
<!--</table>-->

<!--{#if totalCount > connectorsPerPage}-->
<!--  <div>-->
<!--    <button on:click={() => changePage(currentPage - 1)} disabled={currentPage === 1}>上一页</button>-->
<!--    <span>第 {currentPage} 页</span>-->
<!--    <button on:click={() => changePage(currentPage + 1)} disabled={currentPage * connectorsPerPage >= totalCount}>下一页</button>-->
<!--  </div>-->
<!--{/if}-->

<!--<h2>添加数据连接器</h2>-->
<!--<div>-->
<!--  <label for="connector-name">名称:</label>-->
<!--  <input id="connector-name" type="text" bind:value={newConnector.name} />-->

<!--  <label for="connector-url">URL:</label>-->
<!--  <input id="connector-url" type="text" bind:value={newConnector.url} />-->

<!--  <label for="connector-type">类型:</label>-->
<!--  <select id="connector-type" bind:value={newConnector.type}>-->
<!--    <option value="mysql">MySQL</option>-->
<!--    <option value="postgresql">PostgreSQL</option>-->
<!--    <option value="sqlite">SQLite</option>-->
<!--  </select>-->

<!--  <button on:click={addConnector}>添加连接器</button>-->
<!--</div>-->

<!--<script>-->
<!--  // 未来的数据连接器管理功能-->
<!--</script>-->

<!--<h1>数据连接器管理</h1>-->
<!--<p>这里将实现数据连接器的管理功能。</p>-->
