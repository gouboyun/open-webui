<script lang="ts">
	import { getContext } from 'svelte';
	import SearchInput from './SearchInput.svelte';
	import DocumentArrowUpSolid from '$lib/components/icons/DocumentArrowUpSolid.svelte';
	const i18n = getContext('i18n');
	let filesInputElement;

	const uploadFilesHandler = () => {
		filesInputElement.click();
	};
</script>

<div class="relative">
	<button
		class="flex w-full mx-2 items-center px-3 py-2 text-sm font-medium cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl"
		on:click={() => {
			filesInputElement.click();
		}}
	>
		<DocumentArrowUpSolid />
		<div class="line-clamp-1">{$i18n.t('Upload Files')}</div>
	</button>
	<input
		bind:this={filesInputElement}
		type="file"
		hidden
		multiple={false}
		on:change={async () => {
			// if (inputFiles && inputFiles.length > 0) {
			// 	const _inputFiles = Array.from(inputFiles);
			// 	inputFilesHandler(_inputFiles);
			// } else {
			// 	toast.error($i18n.t(`File not found.`));
			// }
			// filesInputElement.value = '';
		}}
	/>

	<SearchInput placeholder={$i18n.t('Search')} />
</div>
