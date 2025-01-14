<script lang="ts">
	import { getContext } from 'svelte';
	import SearchInput from './SearchInput.svelte';
	import DocumentArrowUpSolid from '$lib/components/icons/DocumentArrowUpSolid.svelte';
	import { config , user as _user } from '$lib/stores';
    import { v4 as uuidv4 } from 'uuid';
	import { toast } from 'svelte-sonner';
	import { WEBUI_API_BASE_URL } from '$lib/constants';
	import { transcribeAudio } from '$lib/apis/audio';
	import { blobToFile } from '$lib/utils';
	import { uploadFile } from '$lib/apis/files';
	import FileItem from '$lib/components/common/FileItem.svelte';
	const i18n = getContext('i18n');
	let filesInputElement;
    let inputFiles;
    let files = [];


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
				// 文件上传成功后，自动触发pdf文件内容预览
				

				fileItem.status = 'uploaded';
				fileItem.file = uploadedFile;
				fileItem.id = uploadedFile.id;
				fileItem.collection_name =
					uploadedFile?.meta?.collection_name || uploadedFile?.collection_name;
				fileItem.url = `${WEBUI_API_BASE_URL}/files/${uploadedFile.id}`;

				files = files;
			} else {
				files = files.filter((item) => item?.itemId !== tempItemId);
			}
		} catch (e) {
			toast.error(e);
			files = files.filter((item) => item?.itemId !== tempItemId);
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
    <div>
        <button
            class="flex w-full mx-2 items-center px-3 py-2 text-sm font-medium cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl"
            on:click={() => {
                filesInputElement.click();
            }}
        >
            <DocumentArrowUpSolid />
            <div class="line-clamp-1">{$i18n.t('Upload Files')}</div>
        </button>
    </div>
	
	<input
		bind:this={filesInputElement}
        bind:files={inputFiles}
		type="file"
		hidden
		multiple={false}
		on:change={async () => {
            console.log(inputFiles)
			if (inputFiles && inputFiles.length > 0) {
				const _inputFiles = Array.from(inputFiles);
				inputFilesHandler(_inputFiles);
			} else {
				toast.error($i18n.t(`File not found.`));
			}
			filesInputElement.value = '';
		}}
	/>

	<SearchInput placeholder={$i18n.t('Search')} />
    
    <!-- <FileItem
        item={file}
        url={file.url}
        name={file.name}
        type={file.type}
        size={file?.size}
        colorClassName="bg-white dark:bg-gray-850 "
    /> -->
</div>
