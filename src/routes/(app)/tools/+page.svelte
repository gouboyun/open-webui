<script lang="ts">
	import { goto } from '$app/navigation';
	import Icon from '@iconify/svelte';

	let tools = [
		{
			icon: 'carbon:report',
			title: '公文写手',
			link: '/tools/doc'
		},
		{
			icon: 'carbon:report',
			title: '周报生成',
			link: '/tools/weekreport'
		},
		{
			icon: 'carbon:report',
			title: '核稿工具',
			link: '/tools/proof' 
		},
		{
			icon: 'carbon:report',
			title: '文章润色',
			link: '/tools/polish' 
		},
		{
			icon: 'carbon:report',
			title: 'ppt内容生成器',
			link: '/tools/pptGenerator' 
		},
		{
			icon: 'carbon:report',
			title: '中英互译',
			link: '/tools/translation' 
			
		},
		{
			icon: 'carbon:report',
			title: '文章续写',
			link: '/tools/continueArticle' 
			
		},
		{
			icon: 'carbon:report',
			title: '心理健康导师',
			link: '/tools/psychologist' 
			
		}
	];

	const toPage = (path) => {
		goto(path);
	};
</script>

<div class="  w-full bg-[#efefef] grid grid-cols-6 grid-rows-4">
	{#each tools as tool}
		<button
			on:click={() => {
				toPage(tool.link);
			}}
			class="   flex flex-col justify-center items-center h-40"
		>
			<div
				class="hover:scale-110 w-20 h-20 rounded-full bg-white shadow flex items-center justify-center"
			>
				<Icon icon={tool.icon} font-size={40} color={'#aaa'} />
			</div>

			<div class="text-[1rem] font-bold mt-4 font-primary">{tool.title}</div>
		</button>
	{/each}
</div>
