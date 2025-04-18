## 🌐 Main Blueprint (main_bp)

| Route	       | 	Methods	 | 	Description                               |
|--------------|-----------|--------------------------------------------|
| /		          | 	GET		    | 	Welcome page                              |
| /index	      | 	GET		    | 	Home page with all posts (login required) |
| /sitemap.xml | 	GET		    | 	Dynamically generated sitemap XML         |

## 📝 Posts Blueprint (posts_bp) – Prefix: /post
| Route	           | 	Methods	 | 	Description                |
|------------------|-----------|-----------------------------|
| /post/<post_id>	 | 	GET		    | 	View a specific post by ID |

## 🔐 Auth Blueprint (auth_bp) – Prefix: /auth
| Route	                   | 	Methods	   | 	Description                                   |
|--------------------------|-------------|------------------------------------------------|
| /auth/login	             | 	GET, POST	 | 	Login with username and password              |
| /auth/logout	            | 	GET		      | 	Logout (login required)                       |
| /auth/login/google	      | 	GET		      | 	Redirect to Google OAuth login                |
| /auth/authorize/google	  | 	GET		      | 	Handle Google OAuth callback                  |
| /auth/signup	            | 	GET, POST	 | 	Sign up new user (under development)          |
| /auth/password	          | 	GET, POST	 | 	Request password reset email                  |
| /auth/reset/<token>	     | 	GET, POST	 | 	Reset password with token                     |
| /auth/profile/<user_id>	 | 	GET, POST	 | 	View and update user profile (login required) |
## ⚙️ Admin Blueprint (admin_bp) – Prefix: /admin
| Route	                   | 	Methods	   | 	Description                          |
|--------------------------|-------------|---------------------------------------|
| /admin/	                 | 	GET		      | 	Admin dashboard (admin required)     |
| /admin/add	              | 	GET, POST	 | 	Create new post (login required)     |
| /admin/edit/<post_id>	   | 	GET, POST	 | 	Edit a post (admin and owner only)   |
| /admin/delete/<post_id>	 | 	GET, POST	 | 	Delete a post (admin and owner only) |
