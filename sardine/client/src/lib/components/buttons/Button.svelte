<script lang="ts">
	export let text = 'Hello World';
</script>

<section>
	<button on:click>{text}</button>
</section>

<style>
	button {
		border: solid white 2px;
		background-color: black;
		color: white;
		padding: 8px;
		font-size: 1.2rem;
		margin-left: 15px;
	}

	button:hover {
		background-color: white;
		color: black;
		transition: all 0.2s ease-in-out;
	}
</style>
