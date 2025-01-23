<script lang="ts">
	import type { PDFSlickState, PDFSlick } from '@pdfslick/core';
	import ArrowLeft from '../icons/ArrowLeft.svelte';
	import { showControls, showOverview, currentFileId } from '$lib/stores';
	import XMark from '../icons/XMark.svelte';
	import { createEventDispatcher, getContext, onDestroy, onMount } from 'svelte';
	import { getFileById, getFileContentById } from '$lib/apis/files';

	import Spinner from '$lib/components/common/Spinner.svelte';

	const dispatch = createEventDispatcher();
	let container: HTMLDivElement;
	let RO: ResizeObserver;
	let store: import('zustand/vanilla').StoreApi<PDFSlickState>;
	let pdfSlick: PDFSlick;
	let pdfInit = false;
	let fileLoading = false;

	let tranContainer: HTMLDivElement;
	let tranRO: ResizeObserver;
	let tranStore: import('zustand/vanilla').StoreApi<PDFSlickState>;
	let tranPdfSlick: PDFSlick;
	let tranPdfInit = false;
	let tranFileLoading = false;

	let fileInfo: any = {};
	$: {
		if ($currentFileId && pdfInit) {
			fetchFile();
		}
	}

	let fetchFile = async () => {
		try {
			fileLoading = true;
			tranFileLoading = true;
			let res = await getFileById(localStorage.token, $currentFileId as unknown as string);
			if (!res) return;
			fileInfo = res;
			res = await getFileContentById($currentFileId as unknown as string);
			if (!res) return;
			
			setTimeout(() => {
				const url = URL.createObjectURL(res);
				pdfSlick.loadDocument(url);
				tranPdfSlick.loadDocument(url);
				fileLoading = false;
				tranFileLoading = false;
			}, 500);
		} catch (error) {
			fileLoading = false;
			tranFileLoading = false;
		} 
	};

	onMount(async () => {
		/**
		 * This is all happening on client side, so make sure we load it only there
		 */
		const { create, PDFSlick } = await import('@pdfslick/core');

		/**
		 * Create the PDF Slick store
		 */
		store = create();

		tranStore = create();

		/**
		 * Create the PDF Slick instance
		 */
		pdfSlick = new PDFSlick({
			container,
			store,
			options: {
				scaleValue: 'page-fit'
			}
		});

		tranPdfSlick = new PDFSlick({
			container:tranContainer,
			store: tranStore,
			options: {
				scaleValue: 'page-fit'
			}
		});

		pdfInit = true;
		tranPdfInit	= true;

		// /**
		//  * Load the PDF document
		//  */
		// pdfSlick.loadDocument(url);

		// /**
		//  * Resize observer — if zoom is not an absolute numeric value, adjust the PDF viewer accordingly
		//  */
		RO = new ResizeObserver(() => {
			const { scaleValue } = store.getState();
			if (scaleValue && ['page-width', 'page-fit', 'auto'].includes(scaleValue)) {
				pdfSlick.viewer.currentScaleValue = scaleValue;
			}
		});

		tranRO = new ResizeObserver(() => {
			const { scaleValue } = store.getState();
			if (scaleValue && ['page-width', 'page-fit', 'auto'].includes(scaleValue)) {
				tranPdfSlick.viewer.currentScaleValue = scaleValue;
			}
		});

		// /**
		//  * Subscribe to state changes, and keep values of interest as Svelte writable store,
		//  * or alternatively we could subscribe to just those we need as Svelte vars instead of entire state
		//  *
		//  * Also keep reference of the unsubscribe function we call on component's `onDestroy()` below
		//  */
		// unsubscribe = store.subscribe((s) => {
		// 	pdfSlickStore.set(s);
		// });

		store.setState({ pdfSlick });
		tranStore.setState({ pdfSlick: tranPdfSlick });
	});

	onDestroy(() => {
		/**
		 * Clean up
		 */
		RO?.unobserve(container);
		tranRO?.unobserve(container);

		pdfInit = false;
		tranPdfInit = false;
		// unsubscribe();
	});

	/**
	 * start observing DOM container
	 */
	$: {
		if (RO && container) {
			RO.observe(container);
		}
	}
	$: {
		if (tranRO && tranContainer) {
			tranRO.observe(tranContainer);
		}
	}
</script>

<div class=" w-full h-full relative flex flex-col bg-gray-50 dark:bg-gray-850">
	<div class="w-full flex justify-between items-center shadow bg-[#fefefe]">
		<div class=" pointer-events-none z-50 flex items-center justify-start p-4">
			<button
				class="self-center pointer-events-auto p-1 rounded-full bg-white dark:bg-gray-850"
				on:click={() => {
					showOverview.set(false);
				}}
			>
				<ArrowLeft className="size-3.5  text-gray-900 dark:text-white" />
			</button>
		</div>
		{#if fileInfo?.filename}
			<div
				class=" flex-1
				 text-center whitespace-nowrap text-ellipsis overflow-hidden dark:text-black"
				title={fileInfo?.filename}
			>
				{fileInfo?.filename}
			</div>
		{/if}

		<div class="  pointer-events-none z-50 flex items-center justify-end p-4">
			<button
				class="self-center pointer-events-auto p-1 rounded-full bg-white dark:bg-gray-850"
				on:click={() => {
					dispatch('close');
					localStorage.chatControlsSize = 21;
					showControls.set(false);
					showOverview.set(false);
				}}
			>
				<XMark className="size-3.5 text-gray-900 dark:text-white" />
			</button>
		</div>
	</div>
	<div class=" grid grid-cols-2 py-4 flex-1">
		<div class=" col-span-1 flex relative border-r-2">
			{#if fileLoading}
			<div class="bg-[rgb(100,100,100,0.5)] z-[100] absolute top-0 left-0 w-full h-full flex items-center justify-center">
				<Spinner className="size-10 text-blue-600"/>
			</div>
			{/if}
			<div class="flex-1 relative h-full" id="container">
				<div
					id="viewerContainer"
					class="pdfSlickContainer absolute inset-0 overflow-y-auto"
					bind:this={container}
				>
					<div id="viewer" class="pdfSlickViewer pdfViewer" />
				</div>
			</div>
		</div>

		<div class=" col-span-1 flex relative">
			{#if tranFileLoading}
			<div class="bg-[rgb(100,100,100,0.5)] z-[100] absolute top-0 left-0 w-full h-full flex items-center justify-center">
				<Spinner className="size-10 text-blue-600"/>
			</div>
			{/if}
			<div class="flex-1 relative h-full" id="tranContainer">
				<div
					id="tranViewerContainer"
					class="pdfSlickContainer absolute inset-0 overflow-y-auto"
					bind:this={tranContainer}
				>
					<div id="tranViewer" class="pdfSlickViewer pdfViewer" />
				</div>
			</div>
		</div>
	</div>
</div>
