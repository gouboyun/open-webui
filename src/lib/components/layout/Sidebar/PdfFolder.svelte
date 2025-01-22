<script>
	import { removeFileToPdfById } from '$lib/apis/pdf';
	import FileItem from '$lib/components/common/FileItem.svelte';
	import { createEventDispatcher } from 'svelte';
	import { toast } from 'svelte-sonner';
	import ChevronDown from '../../icons/ChevronDown.svelte';
	import ChevronRight from '../../icons/ChevronRight.svelte';
	import FolderMenu from './Folders/FolderMenu.svelte';
	import EllipsisHorizontal from '$lib/components/icons/EllipsisHorizontal.svelte';
	export let folder;
	export let open = false;

	const dispatch = createEventDispatcher();

	const deleteFileById = async (fileId) => {
		const res = await removeFileToPdfById(localStorage.token, null, fileId).catch((e) => {
			toast.error(e);
			return null;
		});
		if (res) {
			dispatch('change');
		}
	};
</script>

<div class=" w-full">
	{#if folder.name !== '-'}
		<button
			class="px-4 py-2 hover:bg-gray-100 w-full flex items-center mt-1 cursor-pointer group"
			on:click={() => {
				open = !open;
			}}
		>
			{#if open}
				<ChevronDown className=" size-3" strokeWidth="2.5" />
			{:else}
				<ChevronRight className=" size-3" strokeWidth="2.5" />
			{/if}
			<div class=" ml-2 flex-1 flex">
				{folder.name}
			</div>

			<button
				class=" z-10 right-2 invisible group-hover:visible self-center flex items-center dark:text-gray-300"
				on:pointerup={(e) => {
					e.stopPropagation();
				}}
				on:click={(e) => {
					e.stopPropagation();
				}}
			>
				<FolderMenu
					on:rename={() => {
						// editHandler();
					}}
					on:delete={() => {
						//showDeleteConfirm = true;
					}}
					on:export={() => {
						//exportHandler();
					}}
				>
					<button class="p-0.5 dark:hover:bg-gray-850 rounded-lg touch-auto" on:click={(e) => {}}>
						<EllipsisHorizontal className="size-4" strokeWidth="2.5" />
					</button>
				</FolderMenu>
			</button>
		</button>
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
