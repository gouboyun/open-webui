<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import SearchInput from './SearchInput.svelte';
	import DocumentArrowUpSolid from '$lib/components/icons/DocumentArrowUpSolid.svelte';
	import { config, user as _user } from '$lib/stores';
	import { v4 as uuidv4 } from 'uuid';
	import { toast } from 'svelte-sonner';
	import { WEBUI_API_BASE_URL } from '$lib/constants';
	import { transcribeAudio } from '$lib/apis/audio';
	import { blobToFile } from '$lib/utils';
	import { uploadFile } from '$lib/apis/files';
	import FileItem from '$lib/components/common/FileItem.svelte';
	import { addFileToPdfById, deletePdfAll, getPdfList, removeFileToPdfById } from '$lib/apis/pdf';

	import AddContentMenu from '$lib/components/pdf/AddContentMenu.svelte';

	onMount(async () => {
		//await deletePdfAll(localStorage.token);
		await getFiles()
	});
	const i18n = getContext('i18n');
	let filesInputElement;
	let inputFiles;
	let files: any[] = [];

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

		// Check if the file is an audio file and transcribe/convert it to text file
		// if (['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/x-m4a'].includes(file['type'])) {
		// 	const res = await transcribeAudio(localStorage.token, file).catch((error) => {
		// 		toast.error(error);
		// 		return null;
		// 	});

		// 	if (res) {
		// 		console.log(res);
		// 		const blob = new Blob([res.text], { type: 'text/plain' });
		// 		file = blobToFile(blob, `${file.name}.txt`);

		// 		fileItem.name = file.name;
		// 		fileItem.size = file.size;
		// 	}
		// }

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

				// fileItem.status = 'uploaded';
				// fileItem.file = uploadedFile;
				// fileItem.id = uploadedFile.id;
				// fileItem.collection_name =
				// 	uploadedFile?.meta?.collection_name || uploadedFile?.collection_name;
				// fileItem.url = `${WEBUI_API_BASE_URL}/files/${uploadedFile.id}`;

				//files = files;
			} else {
				//files = files.filter((item) => item?.itemId !== tempItemId);
			}
		} catch (e) {
			toast.error(e);
			//files = files.filter((item) => item?.itemId !== tempItemId);
		}
	};

	const addFileHandler = async (fileId) => {
		const res = await addFileToPdfById(localStorage.token, null, fileId).catch((e) => {
			toast.error(e);
			return null;
		});
		if(res){
			await getFiles()
		}

		// if (updatedKnowledge) {
		// 	knowledge = updatedKnowledge;
		// 	toast.success($i18n.t('File added successfully.'));
		// } else {
		// 	toast.error($i18n.t('Failed to add file.'));
		// 	knowledge.files = knowledge.files.filter((file) => file.id !== fileId);
		// }
	};

	const deleteFileById = async (fileId)=>{
		const res = await removeFileToPdfById(localStorage.token, null, fileId).catch((e) => {
			toast.error(e);
			return null;
		});
		if(res){
			await getFiles()
		}
	}

	const getFiles = async () => {
		try {
			const res = await getPdfList(localStorage.token);
			files = res[0].files;
		} catch (e) {
			files = [];
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

			// if (['image/gif', 'image/webp', 'image/jpeg', 'image/png'].includes(file['type'])) {
			// 	if (visionCapableModels.length === 0) {
			// 		toast.error($i18n.t('Selected model(s) do not support image inputs'));
			// 		return;
			// 	}
			// 	let reader = new FileReader();
			// 	reader.onload = async (event) => {
			// 		let imageUrl = event.target.result;

			// 		if ($settings?.imageCompression ?? false) {
			// 			const width = $settings?.imageCompressionSize?.width ?? null;
			// 			const height = $settings?.imageCompressionSize?.height ?? null;

			// 			if (width || height) {
			// 				imageUrl = await compressImage(imageUrl, width, height);
			// 			}
			// 		}

			// 		files = [
			// 			...files,
			// 			{
			// 				type: 'image',
			// 				url: `${imageUrl}`
			// 			}
			// 		];
			// 	};
			// 	reader.readAsDataURL(file);
			// } else {
			uploadFileHandler(file);
			//}
		});
	};
</script>

<div class="relative">

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

	<div
		class="flex-shrink-0 w-full
			flex
			py-2
			rounded-2xl
			border
			border-gray-50
			h-full
			dark:border-gray-850"
	>
		<div class=" flex flex-col w-full space-x-2 rounded-lg h-full">
			<div class="w-full h-full flex flex-col">
				<div class=" pr-3">
					<div class="flex mb-0.5">
						<SearchInput placeholder={$i18n.t('Search')} />
						<div>
							<AddContentMenu
								on:upload={(e) => {
									// if (e.detail.type === 'directory') {
									// 	uploadDirectoryHandler();
									// } else if (e.detail.type === 'text') {
									// 	showAddTextContentModal = true;
									// } else {
									// 	document.getElementById('files-input').click();
									// }
									filesInputElement.click();
								}}
								on:sync={(e) => {
									//showSyncConfirmModal = true;
								}}
							/>
						</div>
					</div>
				</div>

				<!-- {#if filteredItems.length > 0}
					<div class=" flex overflow-y-auto h-full w-full scrollbar-hidden text-xs">
						<Files
							small
							files={filteredItems}
							{selectedFileId}
							on:click={(e) => {
								selectedFileId = selectedFileId === e.detail ? null : e.detail;
							}}
							on:delete={(e) => {
								console.log(e.detail);

								selectedFileId = null;
								deleteFileHandler(e.detail);
							}}
						/>
					</div>
				{:else}
					<div class="my-3 flex flex-col justify-center text-center text-gray-500 text-xs">
						<div>
							{$i18n.t('No content found')}
						</div>
					</div>
				{/if} -->
			</div>
		</div>
	</div>

	
	{#each files as file, fileIdx}
	<div class=" px-4">
		<FileItem
		className="w-full mt-2"
		item={file}
		url={file?.url ? file.url : null}
		name={file.meta.name}
		type={file.meta.content_type}
		size={file?.meta.size}
		dismissible={true}
		on:dismiss={() => {
			deleteFileById(file.id)
			// Remove the file from the chatFiles array

			// chatFiles.splice(fileIdx, 1);
			// chatFiles = chatFiles;
		}}
		on:click={() => {
			console.log(file);
		}}
	/>
	</div>
	
{/each}
	<!-- <FileItem
        item={file}
        url={file.url}
        name={file.name}
        type={file.type}
        size={file?.size}
        colorClassName="bg-white dark:bg-gray-850 "
    /> -->
</div>
