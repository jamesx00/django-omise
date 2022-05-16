module.exports = {
	content: [
		'./django_omise/templates/**/*.{html,js}',
		'./django_omise/static/**/*.js',
	],
	corePlugins: {
		preflight: true,
	},
	darkMode: 'class',
	theme: {
		extend: {},
	},
	plugins: [],
};
