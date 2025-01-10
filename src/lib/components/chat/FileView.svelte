<script lang="ts">
	import type { PDFSlickState, PDFSlick } from '@pdfslick/core';
	import ArrowLeft from '../icons/ArrowLeft.svelte';
	import { showControls, showOverview, currentFileId } from '$lib/stores';
	import XMark from '../icons/XMark.svelte';
	import { createEventDispatcher, getContext, onDestroy, onMount } from 'svelte';
	import { getFileById, getFileContentById } from '$lib/apis/files';

	const dispatch = createEventDispatcher();
	let container: HTMLDivElement;
	let RO: ResizeObserver;
	let store: import('zustand/vanilla').StoreApi<PDFSlickState>;
	let pdfSlick: PDFSlick;
	let pdfInit = false;
	let fileInfo: any = {};
	$: {
		if ($currentFileId && pdfInit) {
			fetchFile();
		}
	}

	let fetchFile = async () => {
		let res = await getFileById(localStorage.token, $currentFileId as unknown as string);
		if (!res) return;
		fileInfo = res;
		res = await getFileContentById($currentFileId as unknown as string);
		if (!res) return;
		const url = URL.createObjectURL(res);
		pdfSlick.loadDocument(url);
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
		pdfInit = true;

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
	});

	onDestroy(() => {
		/**
		 * Clean up
		 */
		RO?.unobserve(container);
		pdfInit = false;
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
	<div class=" py-4 w-full flex flex-1">
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
</div>
