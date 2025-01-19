<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import SearchInput from './SearchInput.svelte';
	import { config, user as _user } from '$lib/stores';
	import { v4 as uuidv4 } from 'uuid';
	import { toast } from 'svelte-sonner';
	import { uploadFile } from '$lib/apis/files';
	import FileItem from '$lib/components/common/FileItem.svelte';
	import { addFileToTranslationsById, getTranslationsFileList, removeTranslationsFileById } from '$lib/apis/translations';

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
				
			} else {
				
			}
		} catch (e) {
			toast.error(e);
		}
	};

	const addFileHandler = async (fileId) => {
		const res = await addFileToTranslationsById(localStorage.token, null, fileId).catch((e) => {
			toast.error(e);
			return null;
		});
		if(res){
			await getFiles()
		}

		
	};

	const deleteFileById = async (fileId)=>{
		const res = await removeTranslationsFileById(localStorage.token, null, fileId).catch((e) => {
			toast.error(e);
			return null;
		});
		if(res){
			await getFiles()
		}
	}

	const getFiles = async () => {
		try {
			const res = await getTranslationsFileList(localStorage.token);
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

			uploadFileHandler(file);
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
									filesInputElement.click();
								}}
								on:sync={(e) => {
									//showSyncConfirmModal = true;
								}}
							/>
						</div>
					</div>
				</div>

				
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
		}}
		on:click={() => {
			console.log(file);
		}}
	/>
	</div>
	
{/each}
	
</div>
