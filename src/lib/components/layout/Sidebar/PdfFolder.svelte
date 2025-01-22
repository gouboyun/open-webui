<script>
	import { removeFileToPdfById } from '$lib/apis/pdf';
	import FileItem from '$lib/components/common/FileItem.svelte';
	import { createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';

	export let folder;

	const dispatch = createEventDispatcher();
	
	const deleteFileById = async (fileId) => {
		const res = await removeFileToPdfById(localStorage.token, null, fileId).catch((e) => {
			toast.error(e);
			return null;
		});
		if (res) {
			dispatch('change')
		}
	};
</script>

<div>
	{#if folder.name !== '-'}
		<div class="px-4">
			{folder.name}
		</div>
	{:else}
		{#each folder.files as node}
			<div class=" px-4">
				<FileItem
					className="w-full mt-2"
					item={node}
					url={node?.url ? node.url : null}
					name={node.meta.name}
					type={node.meta.content_type}
					size={node?.meta.size}
					dismissible={true}
					on:dismiss={() => {
						deleteFileById(node.id);
					}}
					on:click={() => {
						console.log(node);
					}}
				/>
			</div>
		{/each}
	{/if}
</div>
