from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    if current_user.is_authenticated:
        return redirect(url_for('music.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        lembrar = request.form.get('lembrar') == 'on'
        
        resultado = AuthController.fazer_login(email, senha, lembrar)
        
        if resultado['success']:
            flash(resultado['message'], 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('music.index'))
        else:
            flash(resultado['message'], 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('music.index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem', 'error')
            return render_template('register.html')
        
        resultado = AuthController.registrar_usuario(nome, email, senha)
        
        if resultado['success']:
            flash(resultado['message'], 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(resultado['message'], 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Rota de logout"""
    AuthController.fazer_logout()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Rota de perfil do usuário"""
    if request.method == 'POST':
        dados = {
            'nome': request.form.get('nome'),
            'email': request.form.get('email')
        }
        
        resultado = AuthController.atualizar_perfil(current_user, dados)
        
        if resultado['success']:
            flash(resultado['message'], 'success')
        else:
            flash(resultado['message'], 'error')
    
    return render_template('perfil.html', usuario=current_user)

@auth_bp.route('/alterar-senha', methods=['POST'])
@login_required
def alterar_senha():
    """Rota para alteração de senha"""
    senha_atual = request.form.get('senha_atual')
    senha_nova = request.form.get('senha_nova')
    confirmar_senha = request.form.get('confirmar_senha')
    
    if senha_nova != confirmar_senha:
        flash('As senhas não coincidem', 'error')
        return redirect(url_for('auth.perfil'))
    
    resultado = AuthController.alterar_senha(current_user, senha_atual, senha_nova)
    
    if resultado['success']:
        flash(resultado['message'], 'success')
    else:
        flash(resultado['message'], 'error')
    
    return redirect(url_for('auth.perfil'))