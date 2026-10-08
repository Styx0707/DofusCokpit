on(construct){
   while(true)
   {
      if(!(0x27E0124A & 0x27E0124A))
      {
         if(!ord("\b"))
         {
            break;
         }
      }
      else
      {
         §§push("\x06");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      enabled = true;
      html = false;
      multiline = false;
      styleName = "BrownLeftMediumBoldLabel";
      text = "Energie";
      §§push("wordWrap");
      §§push(false);
      if(false)
      {
         §§goto(addr61058);
      }
      break;
   }
   set(§§pop(),§§pop());
   addr61058:
   getProperty(§§pop(), _X);
}
