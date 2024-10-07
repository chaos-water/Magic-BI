<script>
  import { push } from 'svelte-spa-router';

  const options = [
    { name: '对话框', path: '/chat' },
    { name: '文件管理', path: '/file-management' },
    { name: '数据连接器管理', path: '/data-connector' },
    { name: '业务系统管理', path: '/business-system' },
  ];
</script>

<style>
  .option {
    cursor: pointer;
    padding: 10px;
    background-color: #f8f9fa; /* 默认背景色 */
    transition: background-color 0.3s, color 0.3s; /* 添加平滑过渡 */
  }
  .option:hover {
    background-color: #e2e6ea; /* 悬停效果 */
    color: #0056b3; /* 悬停时文字颜色 */
  }
</style>

<div>
  {#each options as option}
    <div class="option" on:click={() => push(option.path)}>
      {option.name}
    </div>
  {/each}
</div>

<!--对这个组件用skeleton进行显示效果优化。-->
<!--有个背景，这个组件被其它组件引用，在副组件中，占据左侧10的显示宽度。-->

<!--<script>-->
<!--  import { push } from 'svelte-spa-router';-->

<!--  const options = [-->
<!--    { name: '对话框', path: '/chat' },-->
<!--    { name: '文件管理', path: '/file-management' },-->
<!--    { name: '数据连接器管理', path: '/data-connector' },-->
<!--    { name: '业务系统管理', path: '/business-system' },-->
<!--  ];-->
<!--</script>-->

<!--<style>-->
<!--  .option {-->
<!--    cursor: pointer;-->
<!--    padding: 10px;-->
<!--  }-->
<!--</style>-->

<!--<div>-->
<!--  {#each options as option}-->
<!--    <div class="option" on:click={() => push(option.path)}>-->
<!--      {option.name}-->
<!--    </div>-->
<!--  {/each}-->
<!--</div>-->
