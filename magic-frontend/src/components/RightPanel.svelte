<script>
  import { httpRequest } from './HttpRequest.svelte';
  import { selectedMode, selectedConnector, selectedDataset } from '../js/store.js';

  const modes = [
    { name: '文档库对话', value: 'rag' },
    { name: '数据库对话', value: 'sql' },
    { name: '业务系统对话', value: 'business_system' },
  ];

  let userId = '';
  let data_connectors = [];
  let datasets = [];
  let loadingConnectors = false; // 加载连接器状态
  let loadingDatasets = false; // 加载数据集合状态

  $: if ($selectedMode === 'sql') {
    fetchConnectors();
  } else if ($selectedMode === 'rag') {
    fetchDatasets();
  }

  async function fetchConnectors() {
    loadingConnectors = true; // 开始加载
    try {
      const ret = await httpRequest('/data_connector/get', 'POST');
      if (ret.code === 0) {
        data_connectors = ret.data.map(item => ({
          name: item.name,
          value: item.id
        }));
        if (data_connectors.length > 0) {}
      }
    } catch (error) {
      console.error('获取连接器失败:', error);
    } finally {
      loadingConnectors = false; // 加载完成
    }
  }

  async function fetchDatasets() {
    loadingDatasets = true; // 开始加载
    try {
      const ret = await httpRequest('/dataset/get', 'POST', { user_id: userId });
      if (ret.code === 0) {
        datasets = ret.data.dataset_list.map(item => ({
          name: item.name,
          value: item.id
        }));
        if (datasets.length > 0) {
          $selectedDataset = datasets[0].value;
        }
      }
    } catch (error) {
      console.error('获取数据集合失败:', error);
    } finally {
      loadingDatasets = false; // 加载完成
    }
  }
</script>

<style>
  .dropdown {
    padding: 10px;
    width: 100%;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  .skeleton {
    background-color: #e0e0e0;
    height: 36px;
    border-radius: 4px;
    margin-bottom: 8px;
    animation: shimmer 1.5s infinite linear;
  }
  @keyframes shimmer {
    0% {
      background-position: -200px 0;
    }
    100% {
      background-position: 200px 0;
    }
  }
</style>

<div>
  <h3>对话模式</h3>
  <select class="dropdown" bind:value={$selectedMode}>
    {#each modes as mode}
      <option value={mode.value}>{mode.name}</option>
    {/each}
  </select>

  {#if $selectedMode === 'sql'}
    <h4>选择数据库连接器:</h4>
    {#if loadingConnectors}
      <div class="skeleton"></div>
    {:else}
      <select class="dropdown" bind:value={$selectedConnector}>
        {#each data_connectors as connector}
          <option value={connector.value}>{connector.name}</option>
        {/each}
      </select>
    {/if}
  {:else if $selectedMode === 'rag'}
    <h4>选择数据集合:</h4>
    {#if loadingDatasets}
      <div class="skeleton"></div>
    {:else}
      <select class="dropdown" bind:value={$selectedDataset}>
        {#each datasets as dataset}
          <option value={dataset.value}>{dataset.name}</option>
        {/each}
      </select>
    {/if}
  {/if}
</div>

<!--<script>-->
<!--  import { httpRequest } from './HttpRequest.svelte'; // 引入http请求功能-->
<!--  import { selectedMode, selectedConnector, selectedDataset } from '../js/store.js';-->

<!--  const modes = [-->
<!--    // { name: '自由对话', value: 'free' },-->
<!--    { name: '文档库对话', value: 'rag' },-->
<!--    { name: '数据库对话', value: 'sql' },-->
<!--    { name: '业务系统对话', value: 'business_system' },-->
<!--  ];-->

<!--  let userId = ''; // 根据实际情况获取 userId-->
<!--  let data_connectors = []; // 存储数据库连接器-->
<!--  let datasets = []; // 存储数据集合-->

<!--  // 监听模式变化-->
<!--  $: if ($selectedMode === 'sql') {-->
<!--    fetchConnectors();-->
<!--  } else if ($selectedMode === 'rag') {-->
<!--    fetchDatasets();-->
<!--  }-->

<!--  async function fetchConnectors() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/data_connector/get', 'POST');-->
<!--      if (ret.code === 0) {-->
<!--        data_connectors = ret.data.map(item => ({-->
<!--        name: item.name, // 假设原字典中有 name 属性-->
<!--        value: item.id   // 假设原字典中有 id 属性-->
<!--        }));-->
<!--        // 如果有可选的连接器，默认选择第一个-->
<!--        console.log("data_connectors:", data_connectors);-->
<!--        if (data_connectors.length > 0) {-->
<!--        }-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取连接器失败:', error);-->
<!--    }-->
<!--  }-->

<!--  async function fetchDatasets() {-->
<!--    try {-->
<!--      const ret = await httpRequest('/dataset/get', 'POST', { user_id: userId });-->
<!--      if (ret.code === 0) {-->
<!--        datasets = ret.data.dataset_list.map(item => ({-->
<!--        name: item.name, // 假设原字典中有 name 属性-->
<!--        value: item.id   // 假设原字典中有 id 属性-->
<!--        }));-->
<!--        // 如果有可选的数据集合，默认选择第一个-->
<!--        console.log("datasets:", datasets);-->
<!--        if (datasets.length > 0) {-->
<!--          $selectedDataset = datasets[0].value;-->
<!--        }-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error('获取数据集合失败:', error);-->
<!--    }-->
<!--  }-->
<!--</script>-->

<!--<style>-->
<!--  .dropdown {-->
<!--    padding: 10px;-->
<!--    width: 100%;-->
<!--  }-->
<!--</style>-->

<!--<div>-->
<!--  <h3>对话模式</h3>-->
<!--  <select class="dropdown" bind:value={$selectedMode}>-->
<!--    {#each modes as mode}-->
<!--      <option value={mode.value}>{mode.name}</option>-->
<!--    {/each}-->
<!--  </select>-->

<!--  {#if $selectedMode === 'sql'}-->
<!--    <h4>选择数据库连接器:</h4>-->
<!--    <select class="dropdown" bind:value={$selectedConnector}>-->
<!--      {#each data_connectors as connector}-->
<!--        <option value={connector.value}>{connector.name}</option>-->
<!--      {/each}-->
<!--    </select>-->
<!--  {:else if $selectedMode === 'rag'}-->
<!--    <h4>选择数据集合:</h4>-->
<!--    <select class="dropdown" bind:value={$selectedDataset}>-->
<!--      {#each datasets as dataset}-->
<!--        <option value={dataset.value}>{dataset.name}</option>-->
<!--      {/each}-->
<!--    </select>-->
<!--  {/if}-->
<!--</div>-->
