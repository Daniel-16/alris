"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen overflow-hidden bg-[#0A0A0F] flex items-center justify-center">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="absolute inset-0">
        <div className="absolute inset-0 opacity-50">
          <div className="fixed top-0 -left-32 w-96 h-96 bg-purple-600/20 rounded-full mix-blend-screen filter blur-[64px] animate-blob animation-delay-2000"></div>
          <div className="fixed bottom-0 -right-32 w-96 h-96 bg-blue-600/20 rounded-full mix-blend-screen filter blur-[64px] animate-blob"></div>
          <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-600/20 rounded-full mix-blend-screen filter blur-[64px] animate-blob animation-delay-4000"></div>
        </div>
      </div>

      <div className="relative z-10 w-full max-w-4xl mx-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="bg-[#12121A] p-8 rounded-xl border border-purple-500/20"
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 via-blue-500 to-purple-600 bg-clip-text text-transparent">
              Privacy Policy
            </h2>
          </div>

          <div className="text-gray-400 space-y-6">
            <section>
              <h3 className="text-xl text-white mb-3">
                1. Information We Collect
              </h3>
              <p>
                We collect several types of information from and about users of
                our Service, including:
              </p>
              <ul className="list-disc pl-6 mt-2 space-y-2">
                <li>
                  Personal Data: Information by which you may be personally
                  identified, such as name, postal address, e-mail address,
                  telephone number, payment information, or any other identifier
                  by which you may be contacted online or offline ("personal
                  information").
                </li>
                <li>
                  Usage Data: Information about your internet connection, the
                  equipment you use to access our Service, usage details,
                  traffic data, logs, communication data, and the resources that
                  you access and use on the Service.
                </li>
                <li>
                  Device Information: Information about your computer, mobile
                  device, browser type and version, operating system, unique
                  device identifiers, and other technical information.
                </li>
                <li>
                  Location Data: Information about your general location as
                  determined from your IP address and other technologies.
                </li>
                <li>
                  Metadata: Information about how and when you use the Service,
                  including time spent on particular pages, click patterns, and
                  other analytics data.
                </li>
              </ul>
            </section>

            <section>
              <h3 className="text-xl text-white mb-3">
                2. How We Use Your Information
              </h3>
              <p>
                We use the information we collect for various purposes,
                including but not limited to:
              </p>
              <ul className="list-disc pl-6 mt-2 space-y-2">
                <li>
                  Providing, operating, maintaining, improving, and promoting
                  the Service
                </li>
                <li>
                  Processing and completing transactions, and sending related
                  information including transaction confirmations and invoices
                </li>
                <li>
                  Sending technical notices, updates, security alerts, and
                  support and administrative messages
                </li>
                <li>
                  Responding to your comments, questions, and requests, and
                  providing customer service and support
                </li>
                <li>
                  Monitoring and analyzing trends, usage, and activities in
                  connection with the Service to improve user experience
                </li>
                <li>
                  Investigating and preventing fraudulent transactions,
                  unauthorized access to the Service, and other illegal
                  activities
                </li>
                <li>
                  Personalizing the Service, including providing features or
                  advertisements that match your interests and preferences
                </li>
                <li>
                  Sending marketing communications, promotional materials, and
                  other notices related to our products, services, and events
                </li>
                <li>
                  For any other purpose with your consent or as otherwise
                  disclosed at the time we collect your information
                </li>
              </ul>
            </section>

            <section>
              <h3 className="text-xl text-white mb-3">
                3. Information Sharing and Disclosure
              </h3>
              <p>
                We may disclose aggregated information about our users and
                information that does not identify any individual without
                restriction. We may disclose personal information that we
                collect or you provide:
              </p>
              <ul className="list-disc pl-6 mt-2 space-y-2">
                <li>
                  To our subsidiaries and affiliates for the purpose of
                  providing the Service
                </li>
                <li>
                  To contractors, service providers, and other third parties we
                  use to support our business operations
                </li>
                <li>
                  To fulfill the purpose for which you provide it, such as
                  registering for an event or entering a contest
                </li>
                <li>
                  To comply with any court order, law, or legal process,
                  including responding to any government or regulatory request
                </li>
                <li>
                  To enforce or apply our terms of use and other agreements
                </li>
                <li>
                  If we believe disclosure is necessary or appropriate to
                  protect the rights, property, or safety of Alris, our
                  customers, or others
                </li>
                <li>
                  To a buyer or other successor in the event of a merger,
                  divestiture, restructuring, reorganization, dissolution, or
                  other sale or transfer of some or all of our assets
                </li>
              </ul>
            </section>

            <section>
              <h3 className="text-xl text-white mb-3">4. Data Security</h3>
              <p>
                We have implemented measures designed to secure your personal
                information from accidental loss and from unauthorized access,
                use, alteration, and disclosure. All information you provide to
                us is stored on secure servers behind firewalls. Any payment
                transactions will be encrypted using SSL technology. However,
                the transmission of information via the internet is not
                completely secure. Although we do our best to protect your
                personal information, we cannot guarantee the security of your
                personal information transmitted to our Service. Any
                transmission of personal information is at your own risk.
              </p>
            </section>

            <section>
              <h3 className="text-xl text-white mb-3">
                5. Your Rights and Choices
              </h3>
              <p>
                Depending on your location and applicable laws, you may have
                certain rights regarding your personal information:
              </p>
              <ul className="list-disc pl-6 mt-2 space-y-2">
                <li>
                  Right to Access: You may request access to your personal
                  information and obtain a copy of personal information we
                  maintain about you
                </li>
                <li>
                  Right to Rectification: You may request that we correct
                  inaccurate or incomplete personal information we maintain
                  about you
                </li>
                <li>
                  Right to Erasure: You may request that we delete your personal
                  information, subject to certain exceptions
                </li>
                <li>
                  Right to Restrict Processing: You may request that we restrict
                  the processing of your personal information in certain
                  circumstances
                </li>
                <li>
                  Right to Data Portability: You may request to receive your
                  personal information in a structured, commonly used, and
                  machine-readable format
                </li>
                <li>
                  Right to Object: You may object to our processing of your
                  personal information based on our legitimate interests and any
                  processing of your personal information for direct marketing
                  purposes
                </li>
              </ul>
            </section>

            <section>
              <h3 className="text-xl text-white mb-3">
                6. Cookies and Tracking Technologies
              </h3>
              <p>
                We use cookies, web beacons, tracking pixels, and other tracking
                technologies to help customize the Service and improve your
                experience. When you access the Service, your personal
                information is not collected through the use of tracking
                technology. Most browsers are set to accept cookies by default.
                You can remove or reject cookies, but be aware that such action
                could affect the availability and functionality of the Service.
                You may not decline web beacons. However, they can be rendered
                ineffective by declining all cookies or by modifying your web
                browser's settings to notify you each time a cookie is tendered,
                permitting you to accept or decline cookies on an individual
                basis.
              </p>
            </section>

            <section>
              <h3 className="text-xl text-white mb-3">
                7. Google Workspace APIs
              </h3>
              <p>
                We expressly confirm and affirm that any data accessed through
                Google Workspace APIs is not used to develop, improve, or train
                generalized artificial intelligence (AI) and/or machine learning
                (ML) models. Our use of Google Workspace APIs is strictly
                limited to providing specific features and functionalities
                within our Service, and we maintain this commitment to protect
                user data and privacy.
              </p>
            </section>

            <section>
              <h3 className="text-xl text-white mb-3">
                8. Changes to This Privacy Policy
              </h3>
              <p>
                We reserve the right to update or change our Privacy Policy at
                any time and you should check this Privacy Policy periodically.
                Your continued use of the Service after we post any
                modifications to the Privacy Policy on this page will constitute
                your acknowledgment of the modifications and your consent to
                abide and be bound by the modified Privacy Policy. If we make
                any material changes to this Privacy Policy, we will notify you
                either through the email address you have provided us or by
                placing a prominent notice on our website.
              </p>
            </section>

            <div className="mt-8 text-center">
              <Link href="/" className="text-purple-500 hover:text-purple-400">
                Return to Home
              </Link>
            </div>
          </div>
        </motion.div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%,
          100% {
            transform: translate(0, 0) scale(1);
          }
          25% {
            transform: translate(20px, -30px) scale(1.1);
          }
          50% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          75% {
            transform: translate(30px, 30px) scale(1.05);
          }
        }

        .animate-blob {
          animation: blob 20s infinite cubic-bezier(0.4, 0, 0.2, 1);
        }

        .animation-delay-2000 {
          animation-delay: 2s;
        }

        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
