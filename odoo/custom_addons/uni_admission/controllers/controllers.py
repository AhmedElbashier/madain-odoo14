# -*- coding: utf-8 -*-
from odoo.http import request, route, Controller, redirect_with_hash
from datetime import date, timedelta
import base64


class Admission(Controller):

	@route('/admission', auth='public', website=True)
	def index(self, **kw):
		return request.render('uni_admission.index')


	# GET|POST /admission/form
	@route('/admission/form', auth='user', website=True, methods=['GET'])
	def form(self, **kw):
		student = request.env['uni.admission'].sudo().search(
			[('user_id', '=', request.env.user.id)],
			limit=1
		)
		print('+++++++++++++++ student')
		if not student:
			return request.render('uni_admission.403')

		country_id = request.env['res.country']
		country_ids = country_id.sudo().search([])

		# A hack to retrieve translated terms
		gender_list = request.env['uni.student']._fields['gender']._description_selection(
			request.env
		)
		religion = request.env['uni.student']._fields['religion']._description_selection(
			request.env
		)
		admission_list = request.env['uni.student']._fields['type_admission']._description_selection(
			request.env
		)
		return request.render('uni_admission.form', {
			'countries': country_ids,
			'student': student,
			'max_date': date.today() - timedelta(days=15*365),
			'gender_list': gender_list,
			'religion': religion,
			'admission_list':admission_list,
			'has_errors': kw.get('has_errors', False)
		})

	@route('/admission/form', auth='user', website=True, methods=['POST'])
	def form_post(self, **kw):
		try:
			student = request.env['uni.admission'].sudo().search(
				[('user_id', '=', request.env.user.id)],
				limit=1
			)

			image = kw['student_id_img']
			if image:
				# Check allowed extensions
				if image.content_type not in ['image/jpeg', 'image/png']:
					raise Exception('We only accept JPG/JPEG/PNG formats')
				image_data = image.read()
				if len(image_data) / (1024.0 * 1024.0) > 8.0:
					raise Exception('Maximum image size exceeded')
				student.sudo().write({
					'student_national_id_img': base64.encodestring(image_data)
				})


			image2 = kw['passport_id_img']
			# Check allowed extensions
			if image2:
				if image2.content_type not in ['image/jpeg', 'image/png']:
					raise Exception('We only accept JPG/JPEG/PNG formats')
				image2_data = image2.read()
				if len(image2_data) / (1024.0 * 1024.0) > 8.0:
					raise Exception('Maximum image size exceeded')
				student.sudo().write({
					'student_passport_id_img': base64.encodestring(image2_data)
				})

			student.write({
				'first_name_en': kw['first_name_en'].strip().title(),
				'middle_name_en': kw['middle_name_en'].strip().title(),
				'last_name_en': kw['last_name_en'].strip().title(),
				'fourth_name_en': kw['fourth_name_en'].strip().title(),
				'type_admission': kw['type_admission'].strip(),
				'birth_date': kw['birth_date'].strip(),
				'place_of_birth': kw['place_of_birth'].strip(),
				'nationality_id': kw['nationality_id'].strip(),
				'gender': kw['gender'].strip(),
				'address': kw['address'].strip(),
				'city': kw['city'].strip(),
				'phone': kw['phone'].strip(),
				'mobile': kw['mobile'].strip(),
				'religion': kw['religion'].strip(),
				'identity_type': kw['identity_type'].strip(),
				'identity_num': kw['identity_num'].strip(),
				
			})

			# Advance to next step
			request.session['admission_step'] = 1
			return redirect_with_hash('/admission/form/family')
		except Exception:
			return redirect_with_hash('/admission/form?has_errors=True')


	@route('/admission/form/family', auth='user', website=True, methods=['GET'])
	def family(self, **kw):
		step = request.session.get('admission_step', 0)

		if step < 1:
			return redirect_with_hash('/admission/form')

		student = request.env['uni.admission'].sudo().search(
				[('user_id', '=', request.env.user.id)],
				limit=1
			)

		if not student:
			return request.render('uni_admission.403')

		admission = request.env['uni.admission'].sudo().search([
			('user_id', '=', request.env.user.id),
			('state', '=', 'candidate')
		])

		try:
			admission.ensure_one()
		except Exception:
			return request.render('uni_admission.form_done')

		return request.render('uni_admission.form_family', {
			'student': student,
			'has_errors': kw.get('has_errors', False)
		})

	@route('/admission/form/family', auth='user', website=True, methods=['POST'])
	def family_post(self, **kw):
		try:
			student = request.env['uni.admission'].sudo().search(
				[('user_id', '=', request.env.user.id)],
				limit=1
			)
			
			student.sudo().write({
				'guardian_ids': [(0,0, {
					'name':kw['guardian_name'].strip(),
					'relation':kw['guardian_relation'].strip(),
					'phone':kw['guardian_phone'].strip(),
					'mobile':kw['guardian_phone2'].strip(),
					'admission_id': student.id,
				})]
			})

			student.sudo().write({
				'guardian_ids': [(0,0, {
					'name': kw['guardian_name2'].strip(),
					'relation': kw['guardian_relation2'].strip(),
					'phone': kw['guardian_phone3'].strip(),
					'mobile': kw['guardian_phone4'].strip(),
					'admission_id': student.id,
				})]
			})


			# Advance to next step
			request.session['admission_step'] = 2
			return redirect_with_hash('/school/certificate')
		except Exception as e:
			return redirect_with_hash('/admission/form/family?has_errors=True')

	#GET|POST /school/certificate
	@route('/school/certificate', auth='user', website=True, methods=['GET'])
	def school_form(self, **kw):

		step = request.session.get('admission_step', 0)

		if step < 2:
			 return redirect_with_hash('/admission/form')

		student = request.env['uni.admission'].sudo().search(
			[('user_id', '=', request.env.user.id)],
			limit=1
		)
		programs = request.env['uni.faculty.program'].sudo().search([])

		if not student:
			return request.render('uni_admission.403')

		return request.render('uni_admission.school_certificate', {
			'student': student,
			'programs':programs,
			'has_errors': kw.get('has_errors', False)
		})

	@route('/school/certificate', auth='user', website=True, methods=['POST'])
	def school_form_post(self, **kw):
		try:
			admission_id = request.env['uni.admission'].sudo().search(
				[('user_id', '=', request.env.user.id)],
				limit=1
			)

			image = kw['scondary_certificate_id_img']
			# Check allowed extensions
			if image.content_type not in ['image/jpeg', 'image/png']:
				raise Exception('We only accept JPG/JPEG/PNG formats')
			image_data = image.read()
			if len(image_data) / (1024.0 * 1024.0) > 8.0:
				raise Exception('Maximum image size exceeded')
			admission_id.sudo().write({
				'scondary_certificate_id_img': base64.encodestring(image_data)
			})

			admission_id.write({
				'admission_year': kw['admission_year'].strip(),
				'school_percentage': kw['school_percentage'].strip(),
				'secondary_school': kw['secondary_school'].strip(),
				'institution_name': kw['institution_name'].strip(),
				'study_years': kw['study_years'].strip(),
				'study_college': kw['study_college'].strip(),
				'study_join_year': kw['study_join_year'].strip(),
				'study_cirtificate_type': kw['study_cirtificate_type'].strip(),
			})

			# Advance to next step
			request.session['admission_step'] = 3
			return redirect_with_hash('/admission/form/photo')
		except Exception:
			return redirect_with_hash('/school/certificate?has_errors=True')

	
	@route('/admission/form/photo', auth='user', website=True, methods=['GET'])
	def photo(self, **kw):
		student = request.env['uni.admission'].sudo().search(
			[('user_id', '=', request.env.user.id)],
			limit=1
		)

		if not student:
			return request.render('uni_admission.403')

		admission = request.env['uni.admission'].sudo().search([
			('user_id', '=', request.env.user.id),
			('state', '=', 'candidate')
		])

		try:
			admission.ensure_one()
		except Exception:
			return request.render('uni_admission.form_done')

		step = request.session.get('admission_step', 0)

		if step < 3:
			return redirect_with_hash('/admission/form')

		return request.render('uni_admission.form_photo', {
			'student':  student,
			'has_errors': kw.get('has_errors', False)
		})

	@route('/admission/form/photo', auth='user', website=True, methods=['POST'])
	def photo_post(self, **kw):
		try:
			image = kw['image']

			# Check allowed extensions
			if image.content_type not in ['image/jpeg', 'image/png']:
				raise Exception('We only accept JPG/JPEG/PNG formats')

			# Check size limit
			image_data = image.read()
			if len(image_data) / (1024.0 * 1024.0) > 8.0:
				raise Exception('Maximum image size exceeded')

			request.env.user.sudo().write({
				'image_1920': base64.encodestring(image_data)
			})
			# TODO: Make image appear in student view
			request.env['uni.admission'].sudo().search(
				[('user_id', '=', request.env.user.id)],
				limit=1).write({
				'std_img': base64.encodestring(image_data)
			}) 
			student = request.env['uni.admission'].sudo().search(
				[('user_id', '=', request.env.user.id)],
				limit=1
			)

			request.env['uni.admission'].sudo().search([
				('user_id', '=', request.env.user.id),
				('state', '=', 'candidate'),
			], limit=1).write({
				'state': 'wait_interview',
			})

			request.session['admission_step'] = 4
			return redirect_with_hash('/admission/form/success')
		except Exception:

			return redirect_with_hash('/admission/form/photo?has_errors=True')

	@route('/admission/form/success', auth='user', website=True )
	def submit(self, **kw):

		step = request.session.get('admission_step', 0)

		if step < 4:
			return redirect_with_hash('/admission/form')

		return request.render('uni_admission.form_success')

