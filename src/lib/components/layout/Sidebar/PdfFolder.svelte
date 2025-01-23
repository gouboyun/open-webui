<script lang="ts">
	import { addFileToPdfById, removePdfFileById, removePdfFolderById } from '$lib/apis/pdf';
	import FileItem from '$lib/components/common/FileItem.svelte';
	import { createEventDispatcher, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import ChevronDown from '../../icons/ChevronDown.svelte';
	import ChevronRight from '../../icons/ChevronRight.svelte';
	import FolderMenu from './Folders/FolderMenu.svelte';
	import EllipsisHorizontal from '$lib/components/icons/EllipsisHorizontal.svelte';
	import DeleteConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import DOMPurify from 'dompurify';
	import { DropdownMenu } from 'bits-ui';
	import ArrowUpCircle from '$lib/components/icons/ArrowUpCircle.svelte';
	import ChatBubble from '$lib/components/icons/ChatBubble.svelte';
	import { config, user as _user } from '$lib/stores';
	import { v4 as uuidv4 } from 'uuid';
	import { uploadFile } from '$lib/apis/files';
	export let folder;
	export let open = false;

	const i18n = getContext('i18n');
	let filesInputElement;
	let inputFiles;
	let showDeleteConfirm = false;

	const dispatch = createEventDispatcher();

	const deleteFileById = async (fileId) => {
		const res = await removePdfFileById(localStorage.token, folder?.id, fileId).catch((e) => {
			toast.error(e);
			return null;
		});
		if (res) {
			dispatch('change');
			toast.success($i18n.t('Success'));
		}
	};

	const deleteFolder = async () => {
		const res = await removePdfFolderById(localStorage.token, folder?.id).catch((e) => {
			toast.error(e);
			return null;
		});
		if (res) {
			dispatch('change');
			toast.success($i18n.t('Success'));
		}
	};

	const uploadFileHandler = async (file, fullContext: boolean = false) => {
		if ($_user?.role !== 'admin' && !($_user?.permissions?.chat?.file_upload ?? true)) {
			toast.error($i18n.t('You do not have permission to upload files.'));
			return null;
		}

		const tempItemId = uuidv4();
		const fileItem = {
			type: 'file',
			file: '',
			id: null,
			url: '',
			name: file.name,
			collection_name: '',
			status: 'uploading',
			size: file.size,
			error: '',
			itemId: tempItemId,
			...(fullContext ? { context: 'full' } : {})
		};

		if (fileItem.size == 0) {
			toast.error($i18n.t('You cannot upload an empty file.'));
			return null;
		}

		try {
			// During the file upload, file content is automatically extracted.
			const uploadedFile = await uploadFile(localStorage.token, file);

			if (uploadedFile) {
				console.log('File upload completed:', {
					id: uploadedFile.id,
					name: fileItem.name,
					collection: uploadedFile?.meta?.collection_name
				});

				if (uploadedFile.error) {
					console.warn('File upload warning:', uploadedFile.error);
					toast.warning(uploadedFile.error);
				}

				await addFileHandler(uploadedFile.id);
				// 文件上传成功后，自动触发pdf文件内容预览
			} else {
			}
		} catch (e) {
			toast.error(e);
		}
	};

	const addFileHandler = async (fileId) => {
		const res = await addFileToPdfById(localStorage.token, folder.id, fileId).catch((e) => {
			toast.error(e);
			return null;
		});
		if (res) {
			dispatch('change');
			toast.success($i18n.t('Success'));
			//await getFiles();
		}
	};

	const inputFilesHandler = async (_files) => {
		console.log('Input files handler called with:', _files);
		_files.forEach((file) => {
			console.log('Processing file:', {
				name: file.name,
				type: file.type,
				size: file.size,
				extension: file.name.split('.').at(-1)
			});

			if (
				($config?.file?.max_size ?? null) !== null &&
				file.size > ($config?.file?.max_size ?? 0) * 1024 * 1024
			) {
				console.log('File exceeds max size limit:', {
					fileSize: file.size,
					maxSize: ($config?.file?.max_size ?? 0) * 1024 * 1024
				});
				toast.error(
					$i18n.t(`File size should not exceed {{maxSize}} MB.`, {
						maxSize: $config?.file?.max_size
					})
				);
				return;
			}

			uploadFileHandler(file);
		});
	};
</script>

<input
	bind:this={filesInputElement}
	bind:files={inputFiles}
	type="file"
	hidden
	multiple={false}
	on:change={async () => {
		console.log(inputFiles);
		if (inputFiles && inputFiles.length > 0) {
			const _inputFiles = Array.from(inputFiles);
			inputFilesHandler(_inputFiles);
		} else {
			toast.error($i18n.t(`File not found.`));
		}
		filesInputElement.value = '';
	}}
/>

<DeleteConfirmDialog
	bind:show={showDeleteConfirm}
	title={$i18n.t('Delete')}
	on:confirm={() => {
		deleteFolder()
	}}
>
	<div class=" text-sm text-gray-700 dark:text-gray-300 flex-1 line-clamp-3">
		{@html DOMPurify.sanitize(
			$i18n.t('This will delete <strong>{{NAME}}</strong> and <strong>all its contents</strong>.', {
				NAME: folder?.name
			})
		)}
	</div>
</DeleteConfirmDialog>

<div class=" w-full">
	{#if folder.name !== '-'}
		<div class="  border-b py-2">
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
				    allowExport={false}
					allowRename={false}
					on:delete={() => {
						showDeleteConfirm = true;
					}}
				>
					<button class="p-0.5 dark:hover:bg-gray-850 rounded-lg touch-auto" on:click={(e) => {}}>
						<EllipsisHorizontal className="size-4" strokeWidth="2.5" />
					</button>

					<div slot="main">
						<DropdownMenu.Item
							class="flex gap-2 items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
							on:click={() => {
								// TODO:
							}}
						>
							<ChatBubble strokeWidth="2" />
							<div class="flex items-center">Chat 目录</div>
						</DropdownMenu.Item>

						<DropdownMenu.Item
							class="flex gap-2 items-center px-3 py-1.5 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
							on:click={() => {
								//dispatch('rename');
								filesInputElement.click();
							}}
						>
							<ArrowUpCircle strokeWidth="2" />
							<div class="flex items-center">{$i18n.t('Upload files')}</div>
						</DropdownMenu.Item>

						
					</div>
				</FolderMenu>
			</button>
		</button>
		{#if open}
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
