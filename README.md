# Simples indicador que mostra as pastas da Home e pastas favoritas

Menu muito simples feito apenas pra suprir a necessidade do usuário acessar rapidamente as pastas da Home

Very simple app-indicator, shows gtk-bookmarks (aka places)

Author: Alex Simenduev <shamil.si@gmail.com>

Modificado para elementaryOS por: http://entornosgnulinux.com/

Portado para **python3** e modificado para stalonetray no Openbox por: http://alexandrecvieira.droppages.com

<img src="http://alexandrecvieira.droppages.com/images/indicator-places/indicator-places.png">

#### Requerimentos

	sudo apt install stalonetray python3-gi gir1.2-appindicator3-0.1 python-appindicator \
	python-gobject python-gobject-2 python3-distutils-extra
	
#### Instalação

	git clone https://github.com/alexandrecvieira/indicator-places.git
	cd indicator-places
	python3 setup.py build
    sudo python3 setup.py install --prefix=/usr
	
	# Configurar para iniciar automaticamente no Openbox
	echo "indicator-places &" >> $HOME/.config/openbox/autostart
